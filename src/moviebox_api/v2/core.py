"""
Main module for v2 submodule.
Generate models from httpx request responses.
Also provides object mapping support to specific extracted item details
"""

from collections.abc import AsyncIterator

from typing_extensions import deprecated

import moviebox_api.v1.core
from moviebox_api.v1.helpers import assert_instance
from moviebox_api.v2._bases import BaseContentProviderAndHelper, BaseItemDetails
from moviebox_api.v2.constants import (
    SINGLE_ITEM_SUBJECT_TYPES,
    SUBJECT_TYPE_CHANNEL_ID_MAP,
    SubjectType,
)
from moviebox_api.v2.exceptions import (
    ExhaustedSearchResultsError,
    MovieboxApiException,
)
from moviebox_api.v2.helpers import get_absolute_url, validate_genre_top_id
from moviebox_api.v2.models import (
    HomepageContentModel,
    RealContentCategoryModel,
    SearchResultsItem,
    SearchResultsModel,
    SpecificItemDetailsModel,
)
from moviebox_api.v2.requests import Session
from moviebox_api.v2.types import FilterParams


class Homepage(moviebox_api.v1.core.Homepage):
    _url = get_absolute_url("/wefeed-h5api-bff/home?host=moviebox.ph")

    async def get_content_model(self) -> HomepageContentModel:
        """Modelled version of the contents"""
        content = await self.get_content()
        return HomepageContentModel(**content)


class MoviesOperatingList(Homepage):
    _url = get_absolute_url(
        "/wefeed-h5api-bff/tab-operating?tabId=ONEROOM_MOVIE&host=h5.aoneroom.com"
    )


class ContentCategory(BaseContentProviderAndHelper):
    _url = get_absolute_url("/wefeed-h5api-bff/ranking-list/content")

    per_page_limit = 50

    def __init__(
        self,
        genre_top_id: str,
        session: Session = None,
        page: int = 1,
        per_page=20,
    ):
        self.session = session
        self._genre_top_id = genre_top_id
        self._page = page
        self._per_page = per_page

    def __setattr__(self, name, value):

        match name:
            case "session":
                assert_instance(value, Session, "session")

            case "_page":
                assert type(value) is int

            case "_per_page":
                assert value <= self.per_page_limit >= 1, (
                    "Value for _per_page must be in the range "
                    f"1-{self.per_page_limit}"
                )

            case "_genre_top_id":
                assert validate_genre_top_id(value), (
                    f"Invalid value for _genre_top_id {value!r}"
                )

            case _:
                pass

        return super().__setattr__(name, value)

    def _create_payload(self) -> dict[str, int | str]:
        return {
            "id": self._genre_top_id,
            "page": self._page,
            "perPage": self._per_page,
        }

    async def get_content(self) -> dict:
        payload = self._create_payload()
        content = await self.session.get_from_api(self._url, params=payload)
        return content

    async def get_content_model(self) -> RealContentCategoryModel:
        content = await self.get_content()
        modelled_content = RealContentCategoryModel.model_validate(content)
        return modelled_content

    def next_page(self, content: RealContentCategoryModel) -> "ContentCategory":
        """Navigate to the search results of the next page.

        Args:
            content (RealContentCategoryModel): Modelled version of search results

        Returns:
            :class:`ContentCategory`
        """
        assert_instance(content, RealContentCategoryModel, "content")

        if content.pager.hasMore:
            return ContentCategory(
                genre_top_id=self._genre_top_id,
                session=self.session,
                page=content.pager.nextPage,
                per_page=self._per_page,
            )
        else:
            raise ExhaustedSearchResultsError(
                content.pager,
                "You have already reached the last page of the search results.",
            )

    def previous_page(
        self, content: RealContentCategoryModel
    ) -> "ContentCategory":
        """Navigate to the search results of the previous page.

        - Useful when the currrent page is greater than  1.

        Args:
            content (RealContentCategoryModel): Modelled version of search results

        Returns:
            :class:`ContentCategory`
        """
        assert_instance(content, RealContentCategoryModel, "content")

        if content.pager.page >= 2:
            return ContentCategory(
                genre_top_id=self._genre_top_id,
                session=self.session,
                per_page=self._per_page,
                page=content.pager.page - 1,
            )
        else:
            raise MovieboxApiException(
                "Unable to navigate to previous page. "
                "Current page is the first one try navigating to the next "
                "one instead."
            )

    async def get_content_model_all(
        self,
    ) -> AsyncIterator[RealContentCategoryModel]:

        navigating = True

        cursor = self

        while navigating:
            content_model = await cursor.get_content_model()

            yield content_model

            if content_model.pager.hasMore:
                cursor = cursor.next_page(content_model)

            else:
                navigating = False


class SearchSuggestion(moviebox_api.v1.core.SearchSuggestion):
    _url = get_absolute_url("/wefeed-h5api-bff/subject/search-suggest")


class Search(moviebox_api.v1.core.Search):
    _url = get_absolute_url("/wefeed-h5api-bff/subject/search")

    async def get_content_model(self) -> SearchResultsModel:
        """Modelled version of the contents.

        Returns:
            SearchResultsModel: Modelled contents
        """
        contents = await self.get_content()
        return SearchResultsModel(**contents)

    @deprecated("This method is only available in v1")
    def get_item_details(self, item: SearchResultsItem) -> None:
        raise NotImplementedError("Method is only available in v1")

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
                "Current page is the first one try navigating to the next "
                "one instead."
            )


class SearchWithFilter(Search):
    """Perform search using filters explicitly - no query string"""

    _url = get_absolute_url("/wefeed-h5api-bff/subject/filter")

    per_page_limit: int = 50

    def __init__(
        self,
        subject_type: SubjectType.MOVIES
        | SubjectType.TV_SERIES
        | SubjectType.ANIME,
        session: Session | None = None,
        filter_params: FilterParams | None = None,
        page: int = 1,
        per_page: int = 24,
    ):
        """Constructor for :class:`SearchWithFilter`

        Args:
            subject_type (SubjectType.MOVIES | SubjectType.TV_SERIES |
              SubjectType.ANIME)
            session (Session, optional): Moviebox-api httpx requests session
            page (int, optional): Target page number. Defaults to 1.
            per_page (int, optional): Maximum items per page. Defaults to 24.
            filter_params (:class:`FilterParams`, optional): Defaults to
                FilterParams()
        """
        self.session = session or Session()
        self._subject_type = subject_type
        self._channel_id: int = None
        self._filter_params = filter_params or FilterParams()
        self._page = page
        self._per_page = per_page

        # for __repr__ consumption
        self._query = filter_params

    def __setattr__(self, name, value):
        match name:
            case "_subject_type":
                assert_instance(value, SubjectType)
                self._channel_id = SUBJECT_TYPE_CHANNEL_ID_MAP[value]

            case "_filter_params":
                assert_instance(value, FilterParams)

            case "session":
                assert_instance(value, Session)

            case "_per_page":
                assert type(value) is int
                assert value <= self.per_page_limit >= 1, (
                    "Value for _per_page must be in the range "
                    f"1-{self.per_page_limit}"
                )

            case "_page":
                assert type(value) is int

            case _:
                pass

        return super().__setattr__(name, value)

    def _create_payload(self) -> dict[str, str | int]:
        """Creates payload from the parameters declared.

        Returns:
            dict[str, str|int]: Ready payload
        """

        filter_params = self._filter_params.model_dump(mode="json")

        filter_params.update({
            "page": self._page,
            "perPage": self._per_page,
            "channelId": self._channel_id,
        })
        return filter_params

    def next_page(self, content: SearchResultsModel) -> "SearchWithFilter":
        """Navigate to the search results of the next page.

        Args:
            content (SearchResultsModel): Modelled version of search results

        Returns:
            :class:`SearchWithFilter`
        """
        assert_instance(content, SearchResultsModel, "content")

        if content.pager.hasMore:
            return SearchWithFilter(
                subject_type=self._subject_type,
                session=self.session,
                page=content.pager.nextPage,
                per_page=self._per_page,
                filter_params=self._filter_params,
            )
        else:
            raise ExhaustedSearchResultsError(
                content.pager,
                "You have already reached the last page of the search results.",
            )

    def previous_page(self, content: SearchResultsModel) -> "SearchWithFilter":
        """Navigate to the search results of the previous page.

        - Useful when the currrent page is greater than  1.

        Args:
            content (SearchResultsModel): Modelled version of search results

        Returns:
            :class:`SearchWithFilter`
        """
        assert_instance(content, SearchResultsModel, "content")

        if content.pager.page >= 2:
            return SearchWithFilter(
                subject_type=self._subject_type,
                session=self.session,
                filter_params=self._filter_params,
                page=content.pager.page - 1,
                per_page=self._per_page,
            )
        else:
            raise MovieboxApiException(
                "Unable to navigate to previous page. "
                "Current page is the first one try navigating to the next "
                "one instead."
            )

    async def get_content_model_all(
        self,
    ) -> AsyncIterator[SearchResultsModel]:

        navigating = True

        cursor = self

        while navigating:
            content_model = await cursor.get_content_model()

            yield content_model

            if content_model.pager.hasMore:
                cursor = cursor.next_page(content_model)

            else:
                navigating = False


class ItemDetails(BaseItemDetails):
    """Fetch specific item details - movies, anime, education,
    music & tv-series"""

    def __init__(self, session: Session):
        """Constructor for `SingleItemDetails`

        Args:
            session (Session): MovieboxAPI request session
        """
        super().__init__(session)

    async def get_content(self, path_or_item: str | SearchResultsItem) -> dict:
        """Get specific item details

        Args:
            path_or_item (str|SearchResultsItem): Detail path for specific item
              page or search-results-item.

        Raises:
            ValueError: InvalidDetailPathError
        """

        assert_instance(path_or_item, (str, SearchResultsItem), "path_or_item")

        detail_path = path_or_item

        if isinstance(path_or_item, SearchResultsItem):
            detail_path = path_or_item.detailPath

        return await super().get_content(detail_path)

    async def get_content_model(
        self, path_or_item: str | SearchResultsItem, **kwargs
    ) -> SpecificItemDetailsModel:

        content = await self.get_content(path_or_item, **kwargs)
        return SpecificItemDetailsModel(**content)


class SingleItemDetails(BaseItemDetails):
    """Fetch specific item details - movies, anime, education, music"""

    def __init__(self, session: Session):
        """Constructor for `SingleItemDetails`

        Args:
            session (Session): MovieboxAPI request session
        """
        super().__init__(session)

    async def get_content(self, path_or_item: str | SearchResultsItem) -> dict:
        """Get specific item details

        Args:
            path_or_item (str|SearchResultsItem): Detail path for specific item
              page or search-results-item.

        Raises:
            ValueError: InvalidDetailPathError
        """

        assert_instance(path_or_item, (str, SearchResultsItem), "path_or_item")

        detail_path = path_or_item

        if isinstance(path_or_item, SearchResultsItem):
            if path_or_item.subjectType == SubjectType.TV_SERIES:
                raise ValueError(
                    "item needs to be any of the following subjectTypes"
                    f"{SINGLE_ITEM_SUBJECT_TYPES!r} "
                    f"not {path_or_item.subjectType!r}"
                )

            detail_path = path_or_item.detailPath

        return await super().get_content(detail_path)

    async def get_content_model(
        self, path_or_item: str | SearchResultsItem, **kwargs
    ) -> SpecificItemDetailsModel:

        content = await self.get_content(path_or_item, **kwargs)
        return SpecificItemDetailsModel(**content)


MusicDetails = AnimeDetails = EducationDetails = MovieDetails = SingleItemDetails


class TVSeriesDetails(BaseItemDetails):
    """Fetch specific item details - tv_series"""

    def __init__(self, session: Session):
        """Constructor for `TVSeriesItemDetails`

        Args:
            session (Session): MovieboxAPI request session
        """
        super().__init__(session)

    async def get_content(self, path_or_item: str | SearchResultsItem) -> dict:
        """Get specific item details

        Args:
            path_or_item (str|SearchResultsItem): Detail path for specific item
              page or search-results-item.

        Raises:
            ValueError: InvalidDetailPathError
        """

        assert_instance(path_or_item, (str, SearchResultsItem), "path_or_item")

        detail_path = path_or_item

        if isinstance(path_or_item, SearchResultsItem):
            if path_or_item.subjectType != SubjectType.TV_SERIES:
                raise ValueError(
                    f"item needs to be of subjectType"
                    f"{SubjectType.TV_SERIES!r} only"
                    f"not {path_or_item.subjectType!r}"
                )

            detail_path = path_or_item.detailPath

        return await super().get_content(detail_path)

    async def get_content_model(
        self, path_or_item: str | SearchResultsItem, **kwargs
    ) -> SpecificItemDetailsModel:

        content = await self.get_content(path_or_item, **kwargs)
        return SpecificItemDetailsModel(**content)
