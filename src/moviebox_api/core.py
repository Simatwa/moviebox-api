"""
Main module for the package.
Generate models from httpx request responses.
Also provides object mapping support to specific extracted item details
"""

import typing as t

from moviebox_api._bases import (
    BaseContentProviderAndHelper,
)
from moviebox_api.constants import SubjectType
from moviebox_api.exceptions import ExhaustedSearchResultsError, MovieboxApiException, ZeroSearchResultsError
from moviebox_api.extractor._core import (
    JsonDetailsExtractor,
    JsonDetailsExtractorModel,
    TagDetailsExtractor,
    TagDetailsExtractorModel,
)
from moviebox_api.extractor.models.json import ItemJsonDetailsModel
from moviebox_api.helpers import (
    assert_instance,
    get_absolute_url,
    get_event_loop,
    is_valid_search_item,
    sanitize_item_name,
    validate_item_page_url,
)
from moviebox_api.models import (
    HomepageContentModel,
    HotMoviesAndTVSeriesModel,
    PopularSearchModel,
    SearchResultsItem,
    SearchResultsModel,
    SuggestedItemsModel,
    TrendingResultsModel,
)
from moviebox_api.requests import Session

__all__ = [
    "Homepage",
    "Search",
    "Trending",
    "Recommend",
    "PopularSearch",
    "MovieDetails",
    "TVSeriesDetails",
    "SearchSuggestion",
    "HotMoviesAndTVSeries",
]


class Homepage(BaseContentProviderAndHelper):
    """Content listings on landing page"""

    _url = get_absolute_url(r"/wefeed-h5-bff/web/home")

    def __init__(self, session: Session):
        """Constructor `Homepage`

        Args:
            session (Session): MovieboxAPI request session
        """
        assert_instance(session, Session, "session")
        self._session = session

    async def get_content(self) -> dict:
        """Landing page contents

        Returns:
            dict
        """
        content = await self._session.get_from_api(self._url)
        return content

    async def get_content_model(self) -> HomepageContentModel:
        """Modelled version of the contents"""
        content = await self.get_content()
        return HomepageContentModel(**content)


class BaseSearch(BaseContentProviderAndHelper):
    """Base class for search providers such as `Trending` and `Search`"""

    session: Session
    """Moviebox-api requests session"""

    _url: str

    def _create_payload(self) -> dict[str, t.Any]:
        raise NotImplementedError("Function needs to be implemented in subclass")

    async def get_content(self) -> dict:
        """Fetches content

        Returns:
            dict: Fetched results
        """
        contents = await self.session.get_with_cookies_from_api(url=self._url, params=self._create_payload())
        return contents

    def get_item_details(self, item: SearchResultsItem) -> "MovieDetails | TVSeriesDetails":
        """Get object that provide more details about the search results item such as casts, seasons etc

        Args:
            item (SearchResultsItem): Search result item

        Returns:
            MovieDetails | TVSeriesDetails: Object providing more details about the item
        """
        assert_instance(item, SearchResultsItem, "item")
        match item.subjectType:
            case SubjectType.MOVIES:
                return MovieDetails(item, self.session)
            case SubjectType.TV_SERIES:
                return TVSeriesDetails(item, self.session)
            case _:
                raise NotImplementedError(
                    f"Currently only items of {SubjectType.MOVIES.name} and {SubjectType.TV_SERIES.name} "
                    "subject-types are supported. Check later versions for possible support of other "
                    "subject-types"
                )


class Search(BaseSearch):
    """Performs a search of movies, tv series, music or all"""

    _url = get_absolute_url(r"/wefeed-h5-bff/web/subject/search")

    def __init__(
        self,
        session: Session,
        query: str,
        subject_type: SubjectType = SubjectType.ALL,
        page: int = 1,
        per_page: int = 24,
    ):
        """Constructor for `Search`

        Args:
            session (Session): MovieboxAPI request session
            query (str): Search query.
            subject_type (SubjectType, optional): Subject-type filter for performing search. Defaults to SubjectType.ALL.
            page (int, optional): Page number filter. Defaults to 1.
            per_page (int, optional): Maximum number of items per page. Defaults to 24.
        """  # noqa: E501
        assert_instance(subject_type, SubjectType, "subject_type")
        assert_instance(session, Session, "session")

        self.session = session
        self._subject_type = subject_type
        self._query = query
        self._page = page
        self._per_page = per_page

    def __repr__(self):
        return (
            rf"<Search query='{self._query}' subject_type={self._subject_type.name} "
            rf"page={self._page} per_page={self._per_page}>"
        )

    async def get_content(self) -> dict:
        """Performs the actual fetch of contents

        Returns:
            dict: Fetched results
        """
        contents = await self.session.post_to_api(url=self._url, json=self._create_payload())

        if self._subject_type is not SubjectType.ALL:
            target_items = []

            # Sometimes server response include irrelevant
            # items

            contents_items = contents["items"]

            if not contents_items:
                raise ZeroSearchResultsError("Search yielded empty results. Try a different keyword.")

            for item in contents_items:
                if item["subjectType"] == self._subject_type.value:
                    # https://github.com/Simatwa/moviebox-api/issues/55
                    item_name = item["title"]

                    if is_valid_search_item(item_name):
                        item["title"] = sanitize_item_name(item_name)
                        target_items.append(item)

            contents["items"] = target_items

        return contents

    async def get_content_model(self) -> SearchResultsModel:
        """Modelled version of the contents.

        Returns:
            SearchResultsModel: Modelled contents
        """
        contents = await self.get_content()
        return SearchResultsModel(**contents)

    def next_page(self, content: SearchResultsModel) -> "Search":
        """Navigate to the search results of the next page.

        Args:
            content (SearchResultsModel): Modelled version of search results

        Returns:
            Search
        """
        assert_instance(content, SearchResultsModel, "content")

        if content.pager.hasMore:
            return Search(
                session=self.session,
                query=self._query,
                subject_type=self._subject_type,
                page=content.pager.nextPage,
                per_page=self._per_page,
            )
        else:
            raise ExhaustedSearchResultsError(
                content.pager,
                "You have already reached the last page of the search results.",
            )

    def previous_page(self, content: SearchResultsModel) -> "Search":
        """Navigate to the search results of the previous page.

        - Useful when the currrent page is greater than  1.

        Args:
            content (SearchResultsModel): Modelled version of search results

        Returns:
            Search
        """
        assert_instance(content, SearchResultsModel, "content")

        if content.pager.page >= 2:
            return Search(
                session=self.session,
                query=self._query,
                subject_type=self._subject_type,
                page=content.pager.page - 1,
                per_page=self._per_page,
            )
        else:
            raise MovieboxApiException(
                "Unable to navigate to previous page. "
                "Current page is the first one try navigating to the next one instead."
            )

    def _create_payload(self) -> dict[str, str | int]:
        """Creates payload from the parameters declared.

        Returns:
            dict[str, str|int]: Ready payload
        """

        return {
            "keyword": self._query,
            "page": self._page,
            "perPage": self._per_page,
            "subjectType": self._subject_type.value,
        }


class Trending(BaseSearch):
    """Trending movies, tv-series and music"""

    _url = get_absolute_url(
        r"/wefeed-h5-bff/web/subject/trending"  # ?uid=5591179548772780352&page=0&perPage=18"
    )

    def __init__(
        self,
        session: Session,
        page: int = 0,
        per_page: int = 18,
    ):
        """Constructor for `Trending`

        Args:
            session (Session): MovieboxAPI request session
            page (int, optional): Page number filter. Defaults to 0.
            per_page (int, optional): Maximum number of items per page. Defaults to 18.
        """
        assert_instance(session, Session, "session")

        self.session = session
        self._page = page
        self._per_page = per_page

    def __repr__(self):
        return rf"<Trending page={self._page} per_page={self._per_page}>"

    async def get_content_model(self) -> TrendingResultsModel:
        """Modelled version of the contents.

        Returns:
            SearchResultsModel: Modelled contents
        """
        contents = await self.get_content()
        return TrendingResultsModel(**contents)

    def next_page(self, content: TrendingResultsModel) -> "Trending":
        """Navigate to the search results of the next page.

        Args:
            content (TrendingResultsModel): Modelled version of search results

        Returns:
            Trending
        """
        assert_instance(content, TrendingResultsModel, "content")

        if content.pager.hasMore:
            return Trending(
                session=self.session,
                page=content.pager.nextPage,
                per_page=self._per_page,
            )
        else:
            raise ExhaustedSearchResultsError(
                content.pager,
                "You have already reached the last page of the search results.",
            )

    def previous_page(self, content: TrendingResultsModel) -> "Trending":
        """Navigate to the search results of the previous page.

        - Useful when the currrent page is greater than  1.

        Args:
            content (TrendingResultsModel): Modelled version of search results

        Returns:
            Trending
        """
        assert_instance(content, TrendingResultsModel, "content")

        if content.pager.page >= 1:  # page starts from 0
            return Trending(
                session=self.session,
                page=content.pager.page - 1,
                per_page=self._per_page,
            )
        else:
            raise MovieboxApiException(
                "Unable to navigate to previous page. "
                "Current page is the first one try navigating to the next one instead."
            )

    def _create_payload(self) -> dict[str, str | int]:
        """Creates payload from the parameters declared.

        Returns:
            dict[str, str|int]: Ready payload
        """

        return {
            "page": self._page,
            "perPage": self._per_page,
        }


class Recommend(BaseSearch):
    """Recommend other movies/tv-series/music based on a given one"""

    _url = get_absolute_url(
        "/wefeed-h5-bff/web/subject/detail-rec"  # ?subjectId=2518237873669820192&page=1&perPage=24"
    )

    def __init__(
        self,
        session: Session,
        item: SearchResultsItem,
        page: int = 1,
        per_page: int = 24,
    ):
        """Constructor for `Recommend`

        Args:
            session (Session): MovieboxAPI request session
            item (SearchResultsItem): Reference item.
            page (int, optional): Page number filter. Defaults to 1.
            per_page (int, optional): Maximum number of items per page. Defaults to 24.
        """
        assert_instance(session, Session, "session")
        assert_instance(item, SearchResultsItem, "item")
        self.session = session
        self._item = item
        self._page = page
        self._per_page = per_page

    def __repr__(self):
        return (
            f"<Recommend item=({self._item.title},{self._item.releaseDate.year} "
            f"page={self._page} per_page={self._per_page}>"
        )

    async def get_content(self) -> dict:
        content = await super().get_content()

        # Just a hack to support pagination - pager attr is missing
        content["pager"] = {
            "hasMore": bool(content.get("items")),  # If it has items then load more
            "nextPage": self._page + 1,
            "page": self._page,
            "perPage": self._per_page,
            "totalCount": 0,
        }
        return content

    async def get_content_model(self) -> SearchResultsModel:
        """Modelled version of the contents.

        Returns:
            SearchResultsModel: Modelled contents
        """
        contents = await self.get_content()
        return SearchResultsModel(**contents)

    def next_page(self, content: SearchResultsModel) -> "Recommend":
        """Navigate to the search results of the next page.

        Args:
            content (SearchResultsModel): Modelled version of search results

        Returns:
            Trending
        """
        assert_instance(content, SearchResultsModel, "content")

        if content.pager.hasMore:
            return Recommend(
                session=self.session,
                item=self._item,
                page=content.pager.nextPage,
                per_page=self._per_page,
            )
        else:
            raise ExhaustedSearchResultsError(
                content.pager,
                "You have already reached the last page of the search results.",
            )

    def previous_page(self, content: SearchResultsModel) -> "Recommend":
        """Navigate to the search results of the previous page.

        - Useful when the currrent page is greater than  1.

        Args:
            content (SearchResultsModel: Modelled version of search results

        Returns:
            Recommend
        """
        assert_instance(content, SearchResultsModel, "content")

        if content.pager.page >= 2:
            return Recommend(
                session=self.session,
                item=self._item,
                page=content.pager.page - 1,
                per_page=self._per_page,
            )
        else:
            raise MovieboxApiException(
                "Unable to navigate to previous page. "
                "Current page is the first one try navigating to the next one instead."
            )

    def _create_payload(self) -> dict[str, str | int]:
        """Creates payload from the parameters declared.

        Returns:
            dict[str, str|int]: Ready payload
        """

        return {
            "page": self._page,
            "subjectId": self._item.subjectId,
            "perPage": self._per_page,
        }


class HotMoviesAndTVSeries(BaseSearch):
    """Hot movies and tv-series"""

    _url = get_absolute_url(r"/wefeed-h5-bff/web/subject/search-rank")

    def __init__(
        self,
        session: Session,
    ):
        """Constructor for `HotMoviesAndTVSeries`

        Args:
            session (Session): MovieboxAPI request session
        """
        assert_instance(session, Session, "session")
        self.session = session

    def _create_payload(self) -> dict:
        return {}

    async def get_content_model(self) -> HotMoviesAndTVSeriesModel:
        contents = await self.get_content()
        return HotMoviesAndTVSeriesModel(**contents)


class PopularSearch(BaseContentProviderAndHelper):
    """Movies and tv-series many people are searching"""

    _url = get_absolute_url(r"/wefeed-h5-bff/web/subject/everyone-search")

    def __init__(self, session: Session):
        """Constructor for `EveryoneSearches`

        Args:
            session (Session): MovieboxAPI request session
        """
        assert_instance(session, Session, "session")
        self._session = session

    async def get_content(self) -> list[dict]:
        """Discover popular items being searched"""
        content = await self._session.get_with_cookies_from_api(url=self._url)
        return content["everyoneSearch"]

    async def get_content_model(self) -> list[PopularSearchModel]:
        """Discover modelled version of popular items being searched"""
        contents = await self.get_content()
        return [PopularSearchModel(**item) for item in contents]


class SearchSuggestion(BaseContentProviderAndHelper):
    """Suggest movie title based on a given text"""

    _url = get_absolute_url(r"/wefeed-h5-bff/web/subject/search-suggest")

    def __init__(self, session: Session, per_page: int = 10):
        """Constructor for `SearchSuggestion`

        Args:
            session (Session): MovieboxAPI request session
            per_page(int, optional): Number of items to suggest. Defauls to 10.
        """

        self.session = session
        self._per_page = per_page

    async def get_content(self, reference: str) -> dict:
        """Get movie suggestions based on a reference

        Args:
            reference (str): Movie keyword or title

        Returns:
            dict: Suggested item(s) details
        """
        contents = await self.session.post_to_api(
            self._url, json={"per_page": self._per_page, "keyword": reference}
        )
        return contents

    async def get_content_model(self, reference: str) -> SuggestedItemsModel:
        """Get movie suggestions based on a reference

        Args:
            reference (str): Movie keyword or title

        Returns:
            SuggestedItemsModel: Modelled suggested item(s) details
        """
        contents = await self.get_content(reference)
        return SuggestedItemsModel(**contents)


class BaseItemDetails(BaseContentProviderAndHelper):
    """Base class for specific movie/tv-series (item) details

    - Page content is fetched only once throughout the life of the instance
    """

    def __init__(self, page_url: str, session: Session):
        """Constructor for `BaseItemPageDetails`

        Args:
            page_url (str): Url to specific page containing the item details.
            session (Session): MovieboxAPI request session
        """
        assert_instance(session, Session, "session")
        self._url = validate_item_page_url(page_url)
        self._session = session
        self.__html_content: str | None = None
        """Cached page contents"""

    async def get_html_content(self) -> str:
        """The specific page contents

        Returns:
            str: html formatted contents of the page
        """
        if self.__html_content is not None:
            # Not a good approach for async but it will save alot of seconds & bandwidth
            return self.__html_content

        resp = await self._session.get_with_cookies(
            get_absolute_url(self._url),
        )
        self.__html_content = resp.text
        return self.__html_content

    async def get_content(self) -> dict[str, t.Any]:
        """Get extracted item details using `self.get_json_details_extractor`

        Returns:
            dict: Item details
        """
        extracted_content = await self.get_json_details_extractor()
        return extracted_content.details

    async def get_content_model(self) -> ItemJsonDetailsModel:
        """Get modelled version of extracted item details using `self.get_json_details_extractor_model`

        Returns:
            ItemJsonDetailsModel: Modelled item details
        """
        modelled_extracted_content = await self.get_json_details_extractor_model()
        return modelled_extracted_content.details

    async def get_tag_details_extractor(self) -> TagDetailsExtractor:
        """Fetch content and return object that provide ways to extract details from html tags of the page"""
        content = await self.get_html_content()
        return TagDetailsExtractor(content)

    async def get_json_details_extractor(self) -> JsonDetailsExtractor:
        """Fetch content and return object that extract details from json-formatted data in the page"""
        html_contents = await self.get_html_content()
        return JsonDetailsExtractor(html_contents)

    async def get_tag_details_extractor_model(self) -> TagDetailsExtractorModel:
        """Fetch content and return object that provide ways to model extracted details from html tags"""
        html_content = await self.get_html_content()
        return TagDetailsExtractorModel(html_content)

    async def get_json_details_extractor_model(
        self,
    ) -> JsonDetailsExtractorModel:
        """Fetch content and return object that models extracted details from json-formatted data in the page"""  # noqa: E501
        html_contents = await self.get_html_content()
        return JsonDetailsExtractorModel(html_contents)

    def get_html_content_sync(self, *args, **kwargs) -> str:
        """Get specific page contents `synchronously`

        Returns:
            str: html formatted contents of the page
        """
        return get_event_loop().run_until_complete(self.get_html_content(*args, **kwargs))

    def get_tag_details_extractor_sync(self, *args, **kwargs) -> TagDetailsExtractor:
        """Synchronously fetch content and return object that provide ways to extract details from html tags of the page"""  # noqa: E501
        return get_event_loop().run_until_complete(self.get_tag_details_extractor(*args, **kwargs))

    def get_json_details_extractor_sync(self, *args, **kwargs) -> JsonDetailsExtractor:
        """Synchronously fetch content and return object that extract details from json-formatted data in the page"""  # noqa: E501
        return get_event_loop().run_until_complete(self.get_json_details_extractor(*args, **kwargs))

    def get_tag_details_extractor_model_sync(self, *args, **kwargs) -> TagDetailsExtractorModel:
        """Synchronously fetch content and return object that provide ways to model extracted details from html tags"""  # noqa: E501
        return get_event_loop().run_until_complete(self.get_tag_details_extractor_model(*args, **kwargs))

    def get_json_details_extractor_model_sync(self, *args, **kwargs) -> JsonDetailsExtractorModel:
        """Synchronously fetch content and return object that models extracted details from json-formatted data in the page"""  # noqa: E501
        return get_event_loop().run_until_complete(self.get_json_details_extractor_model(*args, **kwargs))


class MovieDetails(BaseItemDetails):
    """Specific movie item details"""

    def __init__(self, url_or_item: str | SearchResultsItem, session: Session):
        """Constructor for `MovieDetails`

        Args:
            page_url (str|SearchResultsItem): Url to specific item page or search-results-item.
            session (Session): MovieboxAPI request session
        """
        assert_instance(url_or_item, (str, SearchResultsItem), "url_or_item")

        if isinstance(url_or_item, SearchResultsItem):
            if url_or_item.subjectType != SubjectType.MOVIES:
                raise ValueError(
                    f"item needs to be of subjectType {SubjectType.MOVIES.name} not"
                    f" {url_or_item.subjectType.name}"
                )

            page_url = url_or_item.page_url

        else:
            page_url = url_or_item

        super().__init__(page_url=page_url, session=session)


class TVSeriesDetails(BaseItemDetails):
    """Specific tv-series details"""

    def __init__(self, url_or_item: str | SearchResultsItem, session: Session):
        """Constructor for `TVSeriesDetails`

        Args:
            url_or_item: (str|SearchResultsItem): Url to specific item page or search-results-item.
            session (Session): MovieboxAPI request session
        """
        assert_instance(url_or_item, (str, SearchResultsItem), "url_or_item")

        if isinstance(url_or_item, SearchResultsItem):
            if url_or_item.subjectType != SubjectType.TV_SERIES:
                raise ValueError(
                    f"item needs to be of subjectType {SubjectType.TV_SERIES.name} not "
                    f"{url_or_item.subjectType.name}"
                )

            page_url = url_or_item.page_url

        else:
            page_url = url_or_item

        super().__init__(page_url=page_url, session=session)
