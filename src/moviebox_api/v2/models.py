
from json import loads
from typing import Any

from pydantic import BaseModel, HttpUrl, field_validator

from moviebox_api.v1.models import (
    ContentCategoryModel,
    ContentModel,
    ContentSubjectModel,
    PlatformsModel,
    SearchResultsPagerModel,
)
from moviebox_api.v2.helpers import get_absolute_url


class ContentModelV2(ContentModel):
    subject: 'SearchResultsItem'
    detailPath: str
    url: HttpUrl | None = None

    @field_validator('url', mode='before')
    def validate_url(value: str):
        return value if bool(value) else None


class ContentCategoryBannerModelV2(BaseModel):
    items: list[ContentModelV2]  # list of series/movies


class ContentCategoryModelV2(ContentCategoryModel):
    banner: ContentCategoryBannerModelV2 | None = None
    filters: list[Any]
    customData: Any
    genreTopId: str
    detailPath: str


class HomepageContentModel(BaseModel):
    platformList: list[PlatformsModel]
    operatingList: list[ContentCategoryModelV2]


class OPS(BaseModel):
    """`SearchResultsModel.items[0].ops`"""

    trace_id: str
    search_abt: str
    q: str


class SearchResultsItem(ContentSubjectModel):
    """`SearchResultsModel.items[0]`"""

    subtitles: list[str] | None
    ops: OPS | None 
    hasResource: bool
    imdbRatingCount: int | None = None
    stills: Any = None
    postTitle: str
    season: int
    dubs: list[Any]

    @field_validator("ops", mode="before")
    def validate_ops(value: str) -> dict:
        if not value:
            return

        return loads(value)

    @field_validator("subtitles", mode="before")
    def validate_subtitles(value: str) -> list[str]:
        if not value:
            return

        return value.split(",")

    @property
    def details_url(self) -> str:
        """Url to the specific item details"""
        return get_absolute_url(f"/wefeed-h5api-bff/detail?detailPath={self.detailPath}")


class SearchResultsModel(BaseModel):
    """Whole search results"""

    pager: SearchResultsPagerModel
    items: list[SearchResultsItem]

    @property
    def first_item(self) -> SearchResultsItem:
        return self.items[0]