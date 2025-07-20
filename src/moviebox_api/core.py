""" 
Main module for the package
"""

from moviebox_api.requests import Session
from moviebox_api.utils import assert_instance
from moviebox_api._bases import BaseContentProvider, BaseContentProviderAndHelper
from moviebox_api.models import HomepageContentModel, SearchResults
from moviebox_api.exceptions import ExhaustedSearchResultsError, MovieboxApiException
from typing import Dict
from moviebox_api.utils import SubjectType


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
        self.__content: Dict | None = None

    async def get_content(self) -> Dict:
        """Landing page contents

        Returns:
            Dict
        """
        if self.__content is None:
            await self._update_content()
        return self.__content

    async def _update_content(self, dry: bool = False) -> Dict:
        """Fetch home page contents and update it.

        Args:
            dry (bool): Do not update if previously fetched. Defaults to False.

        Returns:
            Dict: Home contents
        """
        if self.__content is not None and dry == True:
            # Dry update
            pass
        else:
            self.__content = await self.session.get_from_api(self._url)

        return self.__content

    async def get_modelled_content(self) -> HomepageContentModel:
        """Modelled version of the contents"""
        await self._update_content(dry=True)
        return HomepageContentModel(**self.__content)


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


class SearchContent(BaseContentProvider):
    """Performs a search of movies, tv series, music or both"""

    _url = r"https://moviebox.ng/wefeed-h5-bff/web/subject/search"

    def __init__(
        self,
        session: Session,
        keyword: str,
        subject_type: SubjectType = SubjectType.ALL,
        page: int = 1,
        per_page: int = 24,
    ):
        """Constructor for `SearchContent`

        Args:
            session (Session): MovieboxAPI request session
            keyword (str): Search keyword.
            subject_type (SubjectType, optional): Subject-type filter for performing search. Defaults to SubjectType.ALL.
            page (int, optional): Page number filter. Defaults to 1.
            per_page (int, optional): Maximum number of items per page. Defaults to 24.
        """
        assert_instance(subject_type, SubjectType, "subject_type")
        assert_instance(session, Session, "session")
        self.subject_type = subject_type
        self.session = session
        self.keyword = keyword
        self.page = page
        self.per_page = per_page
        self.__latest_content: Dict | None = None
        self.__latest_modelled_content: SearchResults | None = None

    def __repr__(self):
        return (
            rf"<SearchContent keyword='{self.keyword}' subject_type={self.subject_type.name} "
            rf"page={self.page} per_page={self.per_page}>"
        )

    def next_page(self) -> "SearchContent":
        """Navigate to the search results of the next page.

        Returns:
            SearchContent
        """
        if self.__latest_modelled_content is not None:
            if self.__latest_modelled_content.pager.hasMore:
                return SearchContent(
                    session=self.session,
                    keyword=self.keyword,
                    subject_type=self.subject_type,
                    page=self.__latest_modelled_content.pager.nextPage,
                    per_page=self.per_page,
                )
            else:
                raise ExhaustedSearchResultsError(
                    self.__latest_modelled_content.pager,
                    "You have already reached the last page of the search results.",
                )
        else:
            raise MovieboxApiException(
                "Unable to navigate to next page. "
                "Access the contents of current page first before navigating."
            )

    def previous_page(self) -> "SearchContent":
        """Navigate to the search results of the previous page.
        - Useful when the currrent page is greater than  1.
        Returns:
            SearchContent
        """
        if self.__latest_modelled_content is not None:
            if self.__latest_modelled_content.pager.page >= 2:
                return SearchContent(
                    session=self.session,
                    keyword=self.keyword,
                    subject_type=self.subject_type,
                    page=self.__latest_modelled_content.pager.page - 1,
                    per_page=self.per_page,
                )
            else:
                raise MovieboxApiException(
                    "Unable to navigate to previous page. "
                    "Current page is the first one try navigating to the next one instead."
                )
        else:
            raise MovieboxApiException(
                "Unable to navigate to previous page. "
                "Access the contents of current page first before navigating."
            )

    def create_payload(self) -> Dict[str, str | int]:
        """Creates post payload from the parameters declared.

        Returns:
            Dict[str, str|int]: Ready payload
        """
        return {
            "keyword": self.keyword,
            "page": self.page,
            "perPage": self.per_page,
            "subjectType": self.subject_type.value,
        }

    async def get_content(self) -> Dict:
        """Performs search based on the parameters set

        Returns:
            Dict: Search results
        """
        self.__latest_content = await self.session.post_to_api(
            url=self._url, json=self.create_payload()
        )
        return self.__latest_content

    async def get_modelled_content(self, latest: bool = False) -> SearchResults:
        """Modelled version of the contents.

        Args:
            latest(optional, bool) : Whether to return the last fetched contents. Defaults to False.

        Returns:
            SearchResults: Modelled contents
        """
        if latest and self.__latest_content is not None:
            pass
        else:
            await self.get_content()
        self.__latest_modelled_content = SearchResults(**self.__latest_content)
        return self.__latest_modelled_content


Search = SearchContent
