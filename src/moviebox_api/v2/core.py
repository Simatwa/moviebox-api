"""
Main module for v2 submodule.
Generate models from httpx request responses.
Also provides object mapping support to specific extracted item details
"""

import moviebox_api.v1.core
from moviebox_api.v1.helpers import assert_instance
from moviebox_api.v2._bases import BaseItemDetails
from moviebox_api.v2.constants import SINGLE_ITEM_SUBJECT_TYPES, SubjectType
from moviebox_api.v2.helpers import get_absolute_url
from moviebox_api.v2.models import (
    HomepageContentModel,
    SearchResultsItem,
    SearchResultsModel,
    SpecificItemDetailsModel,
)
from moviebox_api.v2.requests import Session


class Homepage(moviebox_api.v1.core.Homepage):
    _url = get_absolute_url("/wefeed-h5api-bff/home?host=moviebox.ph")

    async def get_content_model(self) -> HomepageContentModel:
        """Modelled version of the contents"""
        content = await self.get_content()
        return HomepageContentModel(**content)


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
            detail_path = SearchResultsItem.detailPath

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

            detail_path = SearchResultsItem.detailPath

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

            detail_path = SearchResultsItem.detailPath

        return await super().get_content(detail_path)

    async def get_content_model(
        self, path_or_item: str | SearchResultsItem, **kwargs
    ) -> SpecificItemDetailsModel:

        content = await self.get_content(path_or_item, **kwargs)
        return SpecificItemDetailsModel(**content)
