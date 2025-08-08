"""
Main module for the package.
Generate models from httpx request responses.
Also provides ORM support for a specific extracted item details
"""

from moviebox_api._bases import (
    BaseContentProvider,
    BaseContentProviderAndHelper,
)
from moviebox_api.constants import SubjectType
from moviebox_api.exceptions import (
    ExhaustedSearchResultsError,
    MovieboxApiException,
)
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
    validate_item_page_url,
)
from moviebox_api.models import (
    HomepageContentModel,
    PopularSearchModel,
    SearchResults,
    SearchResultsItem,
)
from moviebox_api.requests import Session

__all__ = ["Homepage", "Search", "PopularSearch", "MovieDetails", "TVSeriesDetails"]


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

    # TODO: Complete this


class Search(BaseContentProvider):
    """Performs a search of movies, tv series, music or all"""

    _url = get_absolute_url(r"/wefeed-h5-bff/web/subject/search")

    # __slots__ = ("session",)

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

    def next_page(self, content: SearchResults) -> "Search":
        """Navigate to the search results of the next page.

        Args:
            content (SearchResults): Modelled version of search results

        Returns:
            Search
        """
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

    def previous_page(self, content: SearchResults) -> "Search":
        """Navigate to the search results of the previous page.

        - Useful when the currrent page is greater than  1.

        Args:
            content (SearchResults): Modelled version of search results

        Returns:
            Search
        """
        assert_instance(content, SearchResults, "content")

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

    def create_payload(self) -> dict[str, str | int]:
        """Creates post payload from the parameters declared.

        Returns:
            dict[str, str|int]: Ready payload
        """

        return {
            "keyword": self._query,
            "page": self._page,
            "perPage": self._per_page,
            "subjectType": self._subject_type.value,
        }

    async def get_content(self) -> dict:
        """Performs search based on the parameters set

        Returns:
            dict: Search results
        """
        contents = await self.session.post_to_api(url=self._url, json=self.create_payload())
        return contents

    async def get_content_model(self) -> SearchResults:
        """Modelled version of the contents.

        Returns:
            SearchResults: Modelled contents
        """
        contents = await self.get_content()
        return SearchResults(**contents)

    def get_item_details(self, item: SearchResultsItem) -> "MovieDetails | TVSeriesDetails":
        """Get object that provide more details of the search results item such as casts, seasons etc

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
            case "_":
                raise ValueError(
                    f"Currently only items of {SubjectType.MOVIES.name} and {SubjectType.TV_SERIES.name} "
                    "subject-types are supported. Check later versions for support of other subject-types"
                )


class BaseItemDetails:
    """Base class for specific movie/tv-series (item) details

    - Page content is fetched only once throughout the life of the instance
    """

    def __init__(self, page_url: str, session: Session):
        """Constructor for `BaseItemPageDetails`

        Args:
            page_url (str): Url to specific page containing the item details.
            session (Session): MovieboxAPI request session
        """
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

        page_contents = await self._session.get_with_cookies(
            get_absolute_url(self._url),
        )
        self.__html_content = page_contents
        return page_contents

    async def get_content(self) -> dict:
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
        return TagDetailsExtractorModel(**html_content)

    async def get_json_details_extractor_model(
        self,
    ) -> JsonDetailsExtractorModel:
        """Fetch content and return object that models extracted details from json-formatted data in the page"""
        html_contents = await self.get_html_content()
        return JsonDetailsExtractorModel(html_contents)


class MovieDetails(BaseItemDetails, BaseContentProviderAndHelper):
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


class TVSeriesDetails(BaseItemDetails, BaseContentProviderAndHelper):
    """Specific tv-series item details"""

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
