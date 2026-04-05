from moviebox_api.v3._bases import BaseContentProviderAndHelper
from moviebox_api.v3.constants import SEARCH_PER_PAGE_LIMIT, SubjectType, TabID
from moviebox_api.v3.exceptions import (
    ExhaustedSearchResultsError,
    MovieboxApiException,
    ZeroSearchResultsError,
)
from moviebox_api.v3.helpers import (
    assert_instance,
    is_valid_search_item,
    sanitize_item_name,
    validate_subject_id,
)
from moviebox_api.v3.http_client import MovieBoxHttpClient
from moviebox_api.v3.models.details import RootItemDetailsModel
from moviebox_api.v3.models.homepage import RootHomepageModel
from moviebox_api.v3.models.search import RootSearchResultsModel


class Homepage(BaseContentProviderAndHelper):
    """Fetches landing page contents"""

    # TODO: Add page navigation

    _path = "/wefeed-mobile-bff/tab-operating"

    def __init__(self, client_session: MovieBoxHttpClient):
        """Constructor for `Homepage`"""
        assert_instance(client_session, MovieBoxHttpClient, "client_session")
        self.client_session = client_session
        self._page_number: int = 1
        self._tab_id: int = 0
        self._version: str = ""

    def _create_params(self) -> dict:
        return {
            "page": self._page_number,
            "tabId": self._tab_id,
            "version": self._version,
        }

    async def get_content(self) -> dict:
        payload = self._create_params()
        contents = await self.client_session.get_from_api(
            self._path, params=payload
        )
        return contents

    async def get_content_model(self, *args, **kwargs) -> RootHomepageModel:
        content = await self.get_content(*args, **kwargs)
        return RootHomepageModel.model_validate(content)


class Search:
    """Performs a search of movies, tv series, music  etc or both"""

    _path = "/wefeed-mobile-bff/subject-api/search/v2"

    def __init__(
        self,
        client_session: MovieBoxHttpClient,
        query: str,
        subject_type: SubjectType = SubjectType.ALL,
        tab_id: TabID = TabID.ALL,
        page: int = 1,
        per_page: int = 20,
    ):
        assert 0 < per_page <= SEARCH_PER_PAGE_LIMIT, (
            f"per_page value {per_page} "
            f"is NOT between 0 and {SEARCH_PER_PAGE_LIMIT}"
        )
        assert_instance(subject_type, SubjectType, "subject_type")
        assert_instance(client_session, MovieBoxHttpClient, "client_session")
        assert_instance(tab_id, TabID, "tab_id")

        self.client_session = client_session
        self._subject_type = subject_type
        self._query = query
        self._page = page
        self._per_page = per_page
        self._tab_id = tab_id

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
            "tabId": self._tab_id,
        }

    async def get_content(self) -> dict:
        """Performs the actual fetch of contents

        Returns:
            dict: Fetched results
        """
        contents = await self.client_session.post_to_api(
            self._path, json=self._create_payload()
        )

        target_items = []

        search_results = contents["results"][0]

        if self._subject_type is not SubjectType.ALL:
            # Sometimes server response include irrelevant
            # items

            for item in search_results["subjects"]:
                if item["subjectType"] == self._subject_type.value:
                    # https://github.com/Simatwa/moviebox-api/issues/55
                    item_name = item["title"]

                    if is_valid_search_item(item_name):
                        item["title"] = sanitize_item_name(item_name)
                        target_items.append(item)
        else:
            target_items = search_results

        contents["items"] = target_items

        if not target_items:
            raise ZeroSearchResultsError(
                "Search yielded empty results. Try a different keyword."
            )

        return contents

    async def get_content_model(self) -> RootSearchResultsModel:
        """Modelled version of the contents.

        Returns:
            RootSearchResultsModel: Modelled contents
        """
        contents = await self.get_content()
        return RootSearchResultsModel.model_validate(contents)

    def next_page(self, content: RootSearchResultsModel) -> "Search":
        """Navigate to the search results of the next page.

        Args:
            content (RootSearchResultsModel): Modelled version of search results

        Returns:
            Search
        """
        assert_instance(content, RootSearchResultsModel, "content")

        if content.pager.has_more:
            return Search(
                client_session=self.client_session,
                query=self._query,
                subject_type=self._subject_type,
                tab_id=self._tab_id,
                page=content.pager.next_page,
                per_page=self._per_page,
            )
        else:
            raise ExhaustedSearchResultsError(
                content.pager,
                "You have already reached the last page of the search results.",
            )

    def previous_page(self, content: RootSearchResultsModel) -> "Search":
        """Navigate to the search results of the previous page.

        - Useful when the currrent page is greater than  1.

        Args:
            content (RootSearchResultsModel): Modelled version of search results

        Returns:
            Search
        """
        assert_instance(content, RootSearchResultsModel, "content")

        if content.pager.page >= 2:
            return Search(
                client_session=self.client_session,
                query=self._query,
                subject_type=self._subject_type,
                tab_id=self._tab_id,
                page=content.pager.page - 1,
                per_page=self._per_page,
            )

        else:
            raise MovieboxApiException(
                "Unable to navigate to previous page. "
                "Current page is the first one try navigating to the next "
                "one instead."
            )


class ItemDetails:
    """Specific item details"""

    _path = "/wefeed-mobile-bff/subject-api/get"

    def __init__(
        self,
        client_session: MovieBoxHttpClient,
    ):
        self.client_session = client_session

    async def get_content(self, subject_id: str) -> dict:
        if not validate_subject_id(subject_id):
            raise ValueError(f"Invalid subject id passed {subject_id!r}")

        request_params = {"subjectId": subject_id}

        contents = await self.client_session.get_from_api(
            self._path, params=request_params
        )

        return contents

    async def get_content_model(self, subject_id: str) -> RootItemDetailsModel:
        contents = await self.get_content(subject_id)

        return RootItemDetailsModel.model_validate(contents)


class BaseDownloadableFilesDetail:
    """Fetches media and subtitle files metadata"""

    _path = "/wefeed-mobile-bff/subject-api/resource"

    def __init__(
        self,
        client_session: MovieBoxHttpClient,
    ):
        self.client_session = client_session

    async def get_content(
        self, subject_id: str, season: int, episode: int
    ) -> dict:
        # seed runtime bearer
        await self.client_session.get_from_api(
            f"/wefeed-mobile-bff/subject-api/get?subjectId={subject_id}"
            )

        request_params = {"subjectId": subject_id, "se": season, "ep": episode}
        contents = await self.client_session.get_from_api(
            self._path, params=request_params
        )
        return contents
