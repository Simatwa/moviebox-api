""" 
Main module for the package
"""
from typing import Dict
from moviebox_api.requests import Session
from moviebox_api.utils import assert_instance
from moviebox_api._bases import BaseContentProvider, BaseContentProviderAndHelper
from moviebox_api.models import HomepageContentModel, SearchResults
from moviebox_api.exceptions import ExhaustedSearchResultsError, MovieboxApiException


class Homepage(BaseContentProviderAndHelper):
    """Content listings on landing page"""

    _url = r"https://moviebox.ng/wefeed-h5-bff/web/home"

    def __init__(self, session: Session):
        """Constructtor `Home`

        Args:
            session (Session): MovieboxAPI request session
        """
        assert_instance(session, Session, "session")
        self.session = session

    async def get_content(self) -> Dict:
        """Landing page contents

        Returns:
            Dict
        """
        content = await self.session.get_from_api(self._url)
        return content

    async def get_modelled_content(self) -> HomepageContentModel:
        """Modelled version of the contents"""
        content = await self.get_content()
        return HomepageContentModel(**content)


class EveryoneSearches(BaseContentProviderAndHelper):
    """Movies and series everyone searches"""

    _url = r"https://moviebox.ng/wefeed-h5-bff/web/subject/everyone-search"

    def __init__(self, session: Session):
        """Constructor for `EveryoneSearches`

        Args:
            session (Session): MovieboxAPI request session
        """
        assert_instance(session, Session, "session")

    # TODO: Complete this


class Search(BaseContentProvider):
    """Performs a search of movies, tv series, music or all"""

    _url = r"https://moviebox.ng/wefeed-h5-bff/web/subject/search"

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
