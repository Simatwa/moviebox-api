"""
Main module for the package. Generate models from httpx request responses.
"""

from typing import Dict

from moviebox_api.requests import Session
from moviebox_api.constants import SubjectType
from moviebox_api.helpers import (
    assert_instance,
    get_absolute_url,
    validate_item_page_url,
)
from moviebox_api._bases import BaseContentProvider, BaseContentProviderAndHelper
from moviebox_api.models import HomepageContentModel, SearchResults, SearchResultsItem
from moviebox_api.exceptions import ExhaustedSearchResultsError, MovieboxApiException

from moviebox_api.extractor._core import (
    JsonDetailsExtractor,
    JsonDetailsExtractorModel,
)
from moviebox_api.extractor.models import ItemDetailsModel


__all__ = ["Homepage", "Search", "MovieDetails", "TVSeriesDetails"]


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

    async def get_content(self) -> Dict:
        """Landing page contents

        Returns:
            Dict
        """
        content = await self._session.get_from_api(self._url)
        return content

    async def get_modelled_content(self) -> HomepageContentModel:
        """Modelled version of the contents"""
        content = await self.get_content()
        return HomepageContentModel(**content)


class EveryoneSearches(BaseContentProviderAndHelper):
    """Movies and tv-series everyone searches"""

    _url = get_absolute_url(r"/wefeed-h5-bff/web/subject/everyone-search")

    def __init__(self, session: Session):
        """Constructor for `EveryoneSearches`

        Args:
            session (Session): MovieboxAPI request session
        """
        assert_instance(session, Session, "session")
        raise NotImplementedError("Not implemented yet. Check later versions")

    # TODO: Complete this


class Search(BaseContentProvider):
    """Performs a search of movies, tv series, music or all"""

    _url = get_absolute_url(r"/wefeed-h5-bff/web/subject/search")

    # __slots__ = ("session",)

    def __init__(
        self,
        session: Session,
        keyword: str,
        subject_type: SubjectType = SubjectType.ALL,
        page: int = 1,
        per_page: int = 24,
    ):
        """Constructor for `Search`

        Args:
            session (Session): MovieboxAPI request session
            keyword (str): Search keyword.
            subject_type (SubjectType, optional): Subject-type filter for performing search. Defaults to SubjectType.ALL.
            page (int, optional): Page number filter. Defaults to 1.
            per_page (int, optional): Maximum number of items per page. Defaults to 24.
        """
        assert_instance(subject_type, SubjectType, "subject_type")
        assert_instance(session, Session, "session")

        self.session = session
        self._subject_type = subject_type
        self._keyword = keyword
        self._page = page
        self._per_page = per_page

    def __repr__(self):
        return (
            rf"<Search keyword='{self._keyword}' subject_type={self._subject_type.name} "
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
                keyword=self._keyword,
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
                keyword=self._keyword,
                subject_type=self._subject_type,
                page=content.pager.page - 1,
                per_page=self._per_page,
            )
        else:
            raise MovieboxApiException(
                "Unable to navigate to previous page. "
                "Current page is the first one try navigating to the next one instead."
            )

    def create_payload(self) -> Dict[str, str | int]:
        """Creates post payload from the parameters declared.

        Returns:
            Dict[str, str|int]: Ready payload
        """

        return {
            "keyword": self._keyword,
            "page": self._page,
            "perPage": self._per_page,
            "subjectType": self._subject_type.value,
        }

    async def get_content(self) -> Dict:
        """Performs search based on the parameters set

        Returns:
            Dict: Search results
        """
        contents = await self.session.post_to_api(
            url=self._url, json=self.create_payload()
        )
        return contents

    async def get_modelled_content(self) -> SearchResults:
        """Modelled version of the contents.

        Returns:
            SearchResults: Modelled contents
        """
        contents = await self.get_content()
        return SearchResults(**contents)


class BaseItemDetails:
    """Base class for specific movie/tv-series (item) details"""

    def __init__(self, page_url: str, session: Session):
        """Constructor for `BaseItemPageDetails`

        Args:
            page_url (str): Url to specific page containing the item details.
            session (Session): MovieboxAPI request session
        """
        self._url = validate_item_page_url(page_url)
        self._session = session

    async def get_html_content(self) -> str:
        """The specific page contents

        Returns:
            str: html formatted contents of the page
        """
        page_contents = await self._session.get_with_cookies(
            get_absolute_url(self._url),
        )
        return page_contents

    async def get_json_extractor(self) -> JsonDetailsExtractor:
        """Fetch content and return instance of `JsonDetailsExtractor`"""
        html_contents = await self.get_html_content()
        return JsonDetailsExtractor(html_contents)

    async def get_modelled_json_extractor(self) -> JsonDetailsExtractorModel:
        """Fetch content and return instance of `JsonDetailsExtractorModel`"""
        html_contents = await self.get_html_content()
        return JsonDetailsExtractorModel(html_contents)

    async def get_content(self) -> Dict:
        """Get extracted item details

        Returns:
            Dict: Item details
        """
        extracted_content = await self.get_json_extractor()
        return extracted_content.details

    async def get_modelled_content(self) -> ItemDetailsModel:
        """Get modelled extracted item details

        Returns:
            ItemDetailsModel: Modelled item details
        """
        modelled_extrated_content = await self.get_modelled_json_extractor()
        return modelled_extrated_content.details


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
                    f"item needs to be of subjectType {SubjectType.MOVIES.name} not {url_or_item.subjectType.name}"
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
            page_url (str|SearchResultsItem): Url to specific item page or search-results-item.
            session (Session): MovieboxAPI request session
        """
        assert_instance(url_or_item, (str, SearchResultsItem), "url_or_item")

        if isinstance(url_or_item, SearchResultsItem):
            if url_or_item.subjectType != SubjectType.TV_SERIES:
                raise ValueError(
                    f"item needs to be of subjectType {SubjectType.TV_SERIES.name} not {url_or_item.subjectType.name}"
                )

            page_url = url_or_item.page_url

        else:
            page_url = url_or_item

        super().__init__(page_url=page_url, session=session)
