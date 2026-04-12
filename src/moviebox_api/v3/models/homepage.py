import json
from datetime import date
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, field_validator

from moviebox_api.v3.constants import SubjectType
from moviebox_api.v3.models.common import MODEL_CONFIG


class Gif(BaseModel):
    model_config = MODEL_CONFIG

    video_url: HttpUrl | None = Field(alias="videoUrl")
    first_frame_url: HttpUrl | None = Field(alias="firstFrameUrl")

    @field_validator("video_url", "first_frame_url", mode="before")
    def validate_url(value):
        return value if bool(value) else None


class Image(BaseModel):
    model_config = MODEL_CONFIG

    url: HttpUrl
    width: int
    height: int
    size: int
    format: str
    thumbnail: str
    gif: Gif | None
    average_hue_light: str | Any = Field(alias="averageHueLight")
    average_hue_dark: str | Any = Field(alias="averageHueDark")


class PlayUrl(BaseModel):
    model_config = MODEL_CONFIG

    play_url: HttpUrl | None = Field(alias="playUrl")
    url_type: str = Field(alias="urlType")

    @field_validator("play_url", mode="before")
    def validate_play_url(value):
        return value if bool(value) else None


class MiniSubjectModel(BaseModel):
    model_config = MODEL_CONFIG

    subject_id: str = Field(alias="subjectId")
    title: str
    release_date: date = Field(alias="releaseDate")
    genre: list[str]
    cover: Image
    subject_type: SubjectType = Field(alias="subjectType")
    detail_url: HttpUrl | None = Field(alias="detailUrl")
    play_url: PlayUrl = Field(alias="playUrl")
    restrict_kid: int = Field(alias="restrictKid")

    @field_validator("genre", mode="before")
    @classmethod
    def split_genre(cls, v):
        if isinstance(v, str):
            return [g.strip() for g in v.split(",") if g.strip()]
        return v

    @field_validator("release_date", mode="before")
    def validate_release_date(value) -> date:
        return date(year=int(value), month=1, day=1)

    @field_validator("detail_url", mode="before")
    def validate_detail_url(value):
        return value if bool(value) else None


class SubjectModel(MiniSubjectModel):
    rate: int
    imdb_rate: str = Field(alias="imdbRate")
    subject_type: SubjectType = Field(alias="subjectType")
    seconds: int
    description: str
    country_name: str = Field(alias="countryName")
    release_date: date = Field(alias="releaseDate")
    seen_status: int = Field(alias="seenStatus")
    viewers: int
    has_resource: bool = Field(alias="hasResource")
    dl: Any
    op_item_id: str = Field(alias="opItemId")
    ops: str
    tag: str
    appointment_date: str = Field(alias="appointmentDate")
    imdb_rating_value: str = Field(alias="imdbRatingValue")
    corner: str
    appointment_cnt: int = Field(alias="appointmentCnt")
    shorts_episode: int = Field(alias="shortsEpisode")

    @field_validator("release_date", mode="before")
    def validate_release_date(value) -> date:
        return date.strptime(value, "%Y-%m-%d")


class BannerItem(BaseModel):
    model_config = MODEL_CONFIG

    image: Image
    content: str
    deep_link: str = Field(alias="deepLink")
    op_item_id: str = Field(alias="opItemId")
    subject_id: str = Field(alias="subjectId")
    has_resource: bool = Field(alias="hasResource")
    seen_status: int = Field(alias="seenStatus")
    subject: MiniSubjectModel | None


class BannerModel(BaseModel):
    model_config = MODEL_CONFIG

    interval: str
    auto_play: bool = Field(alias="autoPlay")
    banners: list[BannerItem]
    style: str


class CustomDataItemModel(BaseModel):
    model_config = MODEL_CONFIG

    image: Image
    content: str
    deep_link: str = Field(alias="deepLink")
    op_item_id: str = Field(alias="opItemId")
    subject_id: str = Field(alias="subjectId")
    has_resource: bool = Field(alias="hasResource")
    seen_status: int = Field(alias="seenStatus")
    subject: MiniSubjectModel | None


class CustomDataModel(BaseModel):
    model_config = MODEL_CONFIG

    row_count: int = Field(alias="rowCount")
    items: list[CustomDataItemModel] | None
    hidden_title: bool = Field(alias="hiddenTitle")


class ItemsModel(BaseModel):
    model_config = MODEL_CONFIG

    type: str
    position: int
    title: str
    groups: list[Any]
    subjects: list[SubjectModel]
    banner: BannerModel | None
    icons: list[Any]
    rankings: list[Any]
    op_id: str = Field(alias="opId")
    deep_link: str = Field(alias="deepLink")
    filters: list[Any]
    custom_data: CustomDataModel | None = Field(alias="customData", default=None)
    play_list_data: Any = Field(alias="playListData")
    ranking_data: Any = Field(alias="rankingData")
    ranking_list_data: Any = Field(alias="rankingListData")
    live_list: list[Any] = Field(alias="liveList")
    page: Any
    post_data: list[Any] = Field(alias="postData")
    version: str
    enable_dedup: int = Field(alias="enableDedup")
    current_page: int = Field(alias="currentPage")


class OpsModel(BaseModel):
    model_config = MODEL_CONFIG

    trace_id: str = Field(alias="trace_id")


class RootHomepageModel(BaseModel):
    model_config = MODEL_CONFIG

    tab_id: int = Field(alias="tabId")
    items: list[ItemsModel]
    version: str
    trending_title: str = Field(alias="trendingTitle")
    ops: OpsModel
    group_pos: int = Field(alias="groupPos")

    @field_validator("ops", mode="before")
    @classmethod
    def parse_ops(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return {}
        return v
