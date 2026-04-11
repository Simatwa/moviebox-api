import json
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, field_validator

from moviebox_api.v3.constants import ResolutionType, SubjectType
from moviebox_api.v3.models.common import MODEL_CONFIG
from moviebox_api.v3.models.homepage import Image
from moviebox_api.v3.models.search import OpsModel, ResultsSubjectModel


class StaffModel(BaseModel):
    model_config = MODEL_CONFIG

    staff_id: str = Field(alias="staffId")
    staff_type: int = Field(alias="staffType")
    name: str
    character: str
    avatar_url: HttpUrl | None = Field(alias="avatarUrl")

    @field_validator("avatar_url", mode="before")
    def validate_avatar_url(value):
        return value if bool(value) else None


class ResolutionModel(BaseModel):
    model_config = MODEL_CONFIG

    episode: int
    title: str
    resource_link: HttpUrl = Field(alias="resourceLink")
    link_type: int = Field(alias="linkType")
    size: int
    upload_by: str = Field(alias="uploadBy")
    resource_id: str = Field(alias="resourceId")
    post_id: str = Field(alias="postId")
    ext_captions: list[Any] = Field(alias="extCaptions")
    se: int
    ep: int
    source_url: HttpUrl = Field(alias="sourceUrl")
    resolution: ResolutionType
    codec_name: str = Field(alias="codecName")
    duration: int
    require_member_type: int = Field(alias="requireMemberType")
    member_icon: str = Field(alias="memberIcon")


class ResourceDetectorModel(BaseModel):
    model_config = MODEL_CONFIG

    type: int
    total_episode: int = Field(alias="totalEpisode")
    total_size: int = Field(alias="totalSize")
    upload_time: str = Field(alias="uploadTime")
    upload_by: str = Field(alias="uploadBy")
    resource_link: HttpUrl = Field(alias="resourceLink")
    download_url: HttpUrl | None = Field(alias="downloadUrl")
    source: str
    first_size: int = Field(alias="firstSize")
    resource_id: str = Field(alias="resourceId")
    post_id: str = Field(alias="postId")
    ext_captions: list[Any] = Field(alias="extCaptions")
    resolution_list: list[ResolutionModel] = Field(alias="resolutionList")
    subject_id: str = Field(alias="subjectId")
    codec_name: str = Field(alias="codecName")

    @field_validator("download_url", mode="before")
    def validate_download_url(value):
        return value if bool(value) else None


class VideoAddressModel(BaseModel):
    model_config = MODEL_CONFIG

    video_id: str = Field(alias="videoId")
    definition: str
    url: HttpUrl
    duration: int
    width: int
    height: int
    size: int
    fps: int
    bitrate: int
    type: int


class TrailerModel(BaseModel):
    model_config = MODEL_CONFIG

    video_address: VideoAddressModel = Field(alias="VideoAddress")
    cover: Image


class DubModel(BaseModel):
    model_config = MODEL_CONFIG

    subject_id: str = Field(alias="subjectId")
    lan_name: str = Field(alias="lanName")
    lan_code: str = Field(alias="lanCode")
    original: bool
    type: int


class StyleModel(BaseModel):
    model_config = MODEL_CONFIG

    col_num: int = Field(alias="colNum")
    shape: str


class ResolutionItemModel(BaseModel):
    model_config = MODEL_CONFIG

    resolution: ResolutionType
    ep_num: int = Field(alias="epNum")


class SeasonItemModel(BaseModel):
    model_config = MODEL_CONFIG

    se: int
    max_ep: int = Field(alias="maxEp")
    all_ep: str = Field(alias="allEp")
    resolutions: list[ResolutionItemModel]

    @property
    def total_episodes(self) -> int:
        return self.max_ep

    @property
    def season_number(self) -> int:
        return self.se

    @property
    def best_resolution(self) -> ResolutionItemModel:
        return self.resolutions[-1]

    @property
    def worst_resolution(self) -> ResolutionItemModel:
        return self.resolutions[1]


class SeasonsModel(BaseModel):
    model_config = MODEL_CONFIG

    subject_id: str = Field(alias="subjectId")
    subject_type: SubjectType = Field(alias="subjectType")
    seasons: list[SeasonItemModel]

    @property
    def total_seasons(self) -> int:
        return len(self.seasons)

    def get_season_by_number(self, number: int) -> SeasonItemModel:
        for season in self.seasons:
            if season.se == number:
                return season

        raise ValueError(f"The item does not have that season number {number}")


class RootItemDetailsModel(ResultsSubjectModel):
    model_config = MODEL_CONFIG

    resource_detectors: list[ResourceDetectorModel] = Field(
        alias="resourceDetectors"
    )
    style: StyleModel
    trailer: TrailerModel
    dubs: list[DubModel]
    staff_list: list[StaffModel] = Field(alias="staffList")
    ops: OpsModel | None
    seasons: SeasonsModel | None

    @field_validator("ops", mode="before")
    def validate_ops(value):
        return json.load(value) if bool(value) else None
