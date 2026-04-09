from collections.abc import AsyncIterator

from moviebox_api.v3._bases import BaseContentProviderAndHelper
from moviebox_api.v3.constants import (
    RESULTS_PER_PAGE_AMOUNT,
    ResolutionType,
    SubjectType,
    TabID,
)
from moviebox_api.v3.exceptions import (
    ExhaustedSearchResultsError,
    ResultsNavigationError,
    ZeroSearchResultsError,
)
from moviebox_api.v3.helpers import (
    assert_instance,
    is_valid_search_item,
    sanitize_item_name,
    validate_per_page_and_raise,
    validate_subject_id,
)
from moviebox_api.v3.http_client import MovieBoxHttpClient
from moviebox_api.v3.models.details import RootItemDetailsModel, SeasonsModel
from moviebox_api.v3.models.downloadables import RootDownloadableFilesDetailModel
from moviebox_api.v3.models.homepage import RootHomepageModel
from moviebox_api.v3.models.search import (
    RootSearchResultsModel,
    RootSearchResultsModelV2,
)
from moviebox_api.v3.urls import (
    MAIN_PAGE_PATH,
    RESOURCE_PATH,
    SEARCH_PATH,
    SEARCH_PATH_V2,
    SEASON_INFO_PATH,
    SUBJECT_GET_PATH,
)


class Homepage(BaseContentProviderAndHelper):
    """Fetches landing page contents"""

    # TODO: Add page navigation

    _path = MAIN_PAGE_PATH

    def __init__(self, client_session: MovieBoxHttpClient):
        """Constructor for `Homepage`"""
        self.client_session = client_session
        self._page_number: int = 1
        self._tab_id: int = 0
        self._version: str = ""

    def __setattr__(self, name, value):
        match name:
            case "client_session":
                assert_instance(value, MovieBoxHttpClient, "client_session")

            case "_per_page":
                validate_per_page_and_raise(value)

            case "_tab_id":
                assert_instance(value, TabID, "tab_id")

            case _:
                pass

        super().__setattr__(name, value)

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


class Search(BaseContentProviderAndHelper):
    """Performs a search of movies, tv series, music  etc or both"""

    _path = SEARCH_PATH

    def __init__(
        self,
        client_session: MovieBoxHttpClient,
        query: str,
        subject_type: SubjectType = SubjectType.ALL,
        page: int = 1,
        per_page: int = RESULTS_PER_PAGE_AMOUNT,
    ):

        self.client_session = client_session
        self._subject_type = subject_type
        self._query = query
        self._page = page
        self._per_page = per_page

    def __setattr__(self, name, value):
        match name:
            case "client_session":
                assert_instance(value, MovieBoxHttpClient, "client_session")

            case "_per_page":
                validate_per_page_and_raise(value)

            case "_subject_type":
                assert_instance(value, SubjectType, "_subject_type")

            case _:
                pass

        super().__setattr__(name, value)

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

    async def get_content(self) -> dict:
        """Performs the actual fetch of contents

        Returns:
            dict: Fetched results
        """
        contents = await self.client_session.post_to_api(
            self._path, json=self._create_payload(), include_play_mode=True
        )

        if self._subject_type is not SubjectType.ALL:
            # Sometimes server response include irrelevant
            # items

            target_items = []

            for item in contents["items"]:
                if item["subjectType"] == self._subject_type.value:
                    # https://github.com/Simatwa/moviebox-api/issues/55
                    item_name = item["title"]

                    if is_valid_search_item(item_name):
                        item["title"] = sanitize_item_name(item_name)
                        target_items.append(item)

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
                page=content.pager.page - 1,
                per_page=self._per_page,
            )

        else:
            raise ResultsNavigationError(
                "Unable to navigate to previous page. "
                "Current page is the first one, try navigating to the next "
                "one instead."
            )


class SearchV2(BaseContentProviderAndHelper):
    """Performs a search of movies, tv series, music  etc or both"""

    _path = SEARCH_PATH_V2

    def __init__(
        self,
        client_session: MovieBoxHttpClient,
        query: str,
        subject_type: SubjectType = SubjectType.ALL,
        tab_id: TabID = TabID.ALL,
        page: int = 1,
        per_page: int = RESULTS_PER_PAGE_AMOUNT,
    ):

        self.client_session = client_session
        self._subject_type = subject_type
        self._query = query
        self._page = page
        self._per_page = per_page
        self._tab_id = tab_id

    def __setattr__(self, name, value):
        match name:
            case "client_session":
                assert_instance(value, MovieBoxHttpClient, "client_session")

            case "_per_page":
                validate_per_page_and_raise(value)

            case "_tab_id":
                assert_instance(value, TabID, "tab_id")

            case "_subject_type":
                assert_instance(value, SubjectType, "subjct_type")

            case _:
                pass

        super().__setattr__(name, value)

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

    async def get_content_model(self) -> RootSearchResultsModelV2:
        """Modelled version of the contents.

        Returns:
            RootSearchResultsModelV2: Modelled contents
        """
        contents = await self.get_content()
        return RootSearchResultsModelV2.model_validate(contents)

    def next_page(self, content: RootSearchResultsModelV2) -> "SearchV2":
        """Navigate to the search results of the next page.

        Args:
            content (RootSearchResultsModelV2): Modelled version of search results

        Returns:
            SearchV2
        """
        assert_instance(content, RootSearchResultsModelV2, "content")

        if content.pager.has_more:
            return SearchV2(
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

    def previous_page(self, content: RootSearchResultsModelV2) -> "SearchV2":
        """Navigate to the search results of the previous page.

        - Useful when the currrent page is greater than  1.

        Args:
            content (RootSearchResultsModelV2): Modelled version of search results

        Returns:
            SearchV2
        """
        assert_instance(content, RootSearchResultsModelV2, "content")

        if content.pager.page >= 2:
            return SearchV2(
                client_session=self.client_session,
                query=self._query,
                subject_type=self._subject_type,
                tab_id=self._tab_id,
                page=content.pager.page - 1,
                per_page=self._per_page,
            )

        else:
            raise ResultsNavigationError(
                "Unable to navigate to previous page. "
                "Current page is the first one, try navigating to the next "
                "one instead."
            )


class SeasonDetails(BaseContentProviderAndHelper):
    """Fetches season information for a particular subject"""

    _path = SEASON_INFO_PATH

    def __init__(
        self,
        client_session: MovieBoxHttpClient,
    ):
        self.client_session = client_session

    def __setattr__(self, name, value):
        match name:
            case "client_session":
                assert_instance(value, MovieBoxHttpClient, "client_session")

            case _:
                pass

        super().__setattr__(name, value)

    async def get_content(self, subject_id: str) -> dict:
        if not validate_subject_id(subject_id):
            raise ValueError(f"Invalid subject id passed {subject_id!r}")

        request_params = {"subjectId": subject_id}

        contents = await self.client_session.get_from_api(
            self._path, params=request_params
        )
        return contents

    async def get_content_model(self, subject_id: str) -> SeasonsModel:
        contents = await self.get_content(subject_id)
        modelled_contents = SeasonsModel.model_validate(contents)
        return modelled_contents


class ItemDetails(BaseContentProviderAndHelper):
    """Specific item details including seasons info"""

    _path = SUBJECT_GET_PATH

    def __init__(
        self, client_session: MovieBoxHttpClient, include_seasons: bool = False
    ):
        self.client_session = client_session
        self.include_seasons = include_seasons
        self.season_details = SeasonDetails(client_session)

    def __setattr__(self, name, value):
        match name:
            case "client_session":
                assert_instance(value, MovieBoxHttpClient, "client_session")

            case "season_details":
                assert_instance(value, SeasonDetails, "season_details")

            case "include_seasons":
                assert type(value) is bool, (
                    f"value for include_seasons must of {type(bool)} not "
                    f"{type(value)}"
                )

            case _:
                pass

        super().__setattr__(name, value)

    async def get_content(
        self,
        subject_id: str,
    ) -> dict:
        if not validate_subject_id(subject_id):
            raise ValueError(f"Invalid subject id passed {subject_id!r}")

        request_params = {"subjectId": subject_id}

        contents = await self.client_session.get_from_api(
            self._path, params=request_params
        )

        seasons = None

        if self.include_seasons:
            seasons = await self.season_details.get_content(subject_id)

        contents["seasons"] = seasons

        return contents

    async def get_content_model(
        self,
        subject_id: str,
    ) -> RootItemDetailsModel:
        contents = await self.get_content(subject_id)

        return RootItemDetailsModel.model_validate(contents)


class DownloadableFilesDetail(BaseContentProviderAndHelper):
    """Fetches media and subtitle files metadata"""

    _path = RESOURCE_PATH

    def __init__(
        self,
        client_session: MovieBoxHttpClient,
        page: int = 1,
        per_page: int = RESULTS_PER_PAGE_AMOUNT,
        resolution: ResolutionType = ResolutionType._1080P,
    ):
        self.client_session = client_session
        self.page = page
        self.per_page = per_page
        self.resolution = resolution

    def __setattr__(self, name, value):
        match name:
            case "client_session":
                assert_instance(value, MovieBoxHttpClient, "client_session")

            case "per_page":
                validate_per_page_and_raise(value)

            case "resolution":
                assert_instance(value, ResolutionType, "resolution")

            case _:
                pass

        super().__setattr__(name, value)

    def _create_params(self, subject_id: str) -> dict:
        validate_subject_id(subject_id)

        return {
            "subjectId": subject_id,
            # "se": season,
            # "ep": episode,
            "resolution": self.resolution,
            "page": self.page,
            "perPage": self.per_page,
            # "all": 0,
            # "startPosition": 1,
            # "endPosition": 1,
            # "pagerMode": 0,
            # "epFrom": 1,
            # "epTo": 1,
        }

    async def get_content(
        self,
        subject_id: str,
    ) -> dict:

        request_params = self._create_params(subject_id)

        contents = await self.client_session.get_from_api(
            self._path,
            params=request_params,
        )
        return contents

    async def get_content_model(
        self, subject_id: str
    ) -> RootDownloadableFilesDetailModel:
        contents = await self.get_content(subject_id)

        modelled_contents = RootDownloadableFilesDetailModel.model_validate(
            contents
        )
        return modelled_contents

    def next_page(
        self, content: RootDownloadableFilesDetailModel
    ) -> "DownloadableFilesDetail":
        """Navigate to the search results of the next page.

        Args:
            content (RootDownloadableFilesDetailModel): Modelled version of search
                results

        Returns:
            DownloadableFilesDetail
        """
        assert_instance(content, RootDownloadableFilesDetailModel, "content")

        if content.pager.has_more:
            return DownloadableFilesDetail(
                client_session=self.client_session,
                page=content.pager.next_page,
                per_page=self.per_page,
                resolution=self.resolution,
            )
        else:
            raise ExhaustedSearchResultsError(
                content.pager,
                "You have already reached the last page of the search results.",
            )

    def previous_page(
        self, content: RootDownloadableFilesDetailModel
    ) -> "DownloadableFilesDetail":
        """Navigate to the search results of the previous page.

        - Useful when the currrent page is greater than  1.

        Args:
            content (RootDownloadableFilesDetailModel): Modelled version of search
              results

        Returns:
            DownloadableFilesDetail
        """
        assert_instance(content, RootDownloadableFilesDetailModel, "content")

        if content.pager.page >= 2:
            return DownloadableFilesDetail(
                client_session=self.client_session,
                page=content.pager.page - 1,
                per_page=self.per_page,
                resolution=self.resolution,
            )

        else:
            raise ResultsNavigationError(
                "Unable to navigate to previous page. "
                "Current page is the first one, try navigating to the next "
                "one instead."
            )

    async def get_content_model_all(
        self, subject_id: str
    ) -> AsyncIterator[RootDownloadableFilesDetailModel]:

        navigating = True

        cursor = self

        while navigating:
            content_model = await cursor.get_content_model(subject_id)

            yield content_model

            if content_model.pager.has_more:
                cursor = cursor.next_page(content_model)

            else:
                navigating = False
