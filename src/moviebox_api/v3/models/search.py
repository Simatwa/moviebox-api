import json
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, field_validator

from moviebox_api.v3.constants import SubjectType, TabID, TopicType
from moviebox_api.v3.models.common import MODEL_CONFIG
from moviebox_api.v3.models.homepage import Image, PlayUrl


class VerticalRankItem(BaseModel):
    model_config = MODEL_CONFIG

    title: str
    description: str
    cover: Image
    deeplink: str
    count: int
    is_force_insert: bool = Field(alias="isForceInsert")


class OpsModel(BaseModel):
    model_config = MODEL_CONFIG

    trace_id: str = Field(alias="trace_id")
    rid: str
    search_abt: str = Field(alias="search_abt")
    q: str


class ResultsSubjectModel(BaseModel):
    model_config = MODEL_CONFIG

    subject_id: str = Field(alias="subjectId")
    subject_type: SubjectType = Field(alias="subjectType")
    title: str
    description: str
    release_date: date = Field(alias="releaseDate")
    duration: str
    genre: list[str]
    cover: Image | None
    pre_video_cover: Any = Field(alias="preVideoCover")
    pre_video_address: list[Any] = Field(alias="preVideoAddress")
    country_name: str = Field(alias="countryName")
    language: list[str]
    imdb_rating_value: float = Field(alias="imdbRatingValue")
    staff_list: list[Any] = Field(alias="staffList")
    want_to_see_count: int = Field(alias="wantToSeeCount")
    have_seen_count: int = Field(alias="haveSeenCount")
    seen_status: int = Field(alias="seenStatus")
    my_see_time: str = Field(alias="mySeeTime")
    my_score_value: int = Field(alias="myScoreValue")
    my_score_post_id: str = Field(alias="myScorePostId")
    my_score_time: str = Field(alias="myScoreTime")
    opt: str
    has_resource: bool = Field(alias="hasResource")
    resource_detectors: list[Any] = Field(alias="resourceDetectors")
    ops: OpsModel
    duration_seconds: int = Field(alias="durationSeconds")
    stills: Image | None
    trailer: Any
    content_rating: str = Field(alias="contentRating")
    post_title: str = Field(alias="postTitle")
    aka: str
    explains: list[Any]
    season_numbers: int = Field(alias="seNum")
    viewers: int
    category: str
    subtitles: list[str]
    dubs: list[Any]
    related_app: Any = Field(alias="relatedApp")
    restrict_level: str = Field(alias="restrictLevel")
    corner: str
    like_status: int = Field(alias="likeStatus")
    style: Any
    detail_url: HttpUrl | None = Field(alias="detailUrl")
    play_url: PlayUrl | None = Field(alias="playUrl")
    restrict_kid: int = Field(alias="restrictKid")
    season: int
    is_cam: bool = Field(alias="isCam")

    @property
    def total_seasons(self) -> int:
        "Total number of seasons"
        return self.season_numbers

    @property
    def is_accessible_from_website(self) -> bool:
        """Whether this movie is accessible from
        Moviebox website
        """
        return self.detail_url is not None

    @field_validator("genre", "language", "subtitles", mode="before")
    @classmethod
    def split_genre(cls, v):
        if isinstance(v, str):
            return [g.strip() for g in v.split(",") if g.strip()]
        return v

    @field_validator("ops", mode="before")
    @classmethod
    def parse_ops(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return {}
        return v

    @field_validator("detail_url", "play_url", mode="before")
    def validate_detail_url(value):
        return value if bool(value) else None

    @field_validator("imdb_rating_value", mode="before")
    def validate_imdb_rating_value(value):
        return float(value) if bool(value) else 0

    @field_validator("release_date", mode="before")
    def validate_release_date(value) -> date:
        return datetime.strptime(value, "%Y-%m-%d").date()


class SearchResultsItem(BaseModel):
    model_config = MODEL_CONFIG

    topic_type: TopicType = Field(alias="topicType")
    subjects: list[ResultsSubjectModel]
    staffs: list[Any]
    groups: list[Any]
    vertical_ranks: list[VerticalRankItem] = Field(alias="verticalRanks")
    title: str
    show_more: bool = Field(alias="showMore")
    more_tab_id: TabID | None = Field(alias="moreTabId")

    @field_validator("more_tab_id", mode="before")
    def validate_more_tab_id(value):
        return value if bool(value) else None


class PagerModel(BaseModel):
    model_config = MODEL_CONFIG

    has_more: bool = Field(alias="hasMore")
    next_page: int = Field(alias="nextPage")
    page: int
    per_page: int = Field(alias="perPage")
    total_count: int = Field(alias="totalCount")


class RootSearchResultsModelV2(BaseModel):
    model_config = MODEL_CONFIG

    pager: PagerModel
    results: list[SearchResultsItem]
    tab_id: TabID = Field(alias="tabId")
    tabs: list[Any]
    items: list[ResultsSubjectModel]  # Script generated

    @property
    def first_item(self) -> ResultsSubjectModel:
        return self.items[0]


class RootSearchResultsModel(BaseModel):
    model_config = MODEL_CONFIG

    pager: PagerModel
    vertical_ranks: list[VerticalRankItem] = Field(alias="verticalRanks")
    items: list[ResultsSubjectModel]
    counts: list[dict]
    subject_type: SubjectType = Field(alias="subjectType")
    staffs: list[Any]
    accurate: Any

    @property
    def first_item(self) -> ResultsSubjectModel:
        return self.items[0]
