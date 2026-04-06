from typing import Any

from pydantic import BaseModel, Field, HttpUrl, field_validator

from moviebox_api.v3.constants import ResolutionType, SubjectType
from moviebox_api.v3.models.common import MODEL_CONFIG
from moviebox_api.v3.models.search import Image, PagerModel


class DownloadItemModel(BaseModel):
    model_config = MODEL_CONFIG

    episode: int
    title: str
    resource_link: HttpUrl = Field(alias="resourceLink")
    link_type: int = Field(alias="linkType")
    size: str
    upload_by: str = Field(alias="uploadBy")
    resource_id: str = Field(alias="resourceId")
    post_id: str = Field(alias="postId")
    ext_captions: list[Any] = Field(alias="extCaptions")
    se: int
    ep: int
    source_url: HttpUrl = Field(alias="sourceUrl")
    resolution: int
    codec_name: str = Field(alias="codecName")
    duration: int
    require_member_type: int = Field(alias="requireMemberType")
    member_icon: str = Field(alias="memberIcon")


class CollectionResolutionModel(BaseModel):
    model_config = MODEL_CONFIG

    resolution: ResolutionType
    average_size: str = Field(alias="averageSize")
    ep_num: int = Field(alias="epNum")
    require_member_type: int = Field(alias="requireMemberType")
    member_icon: str = Field(alias="memberIcon")


class RootDownloadFilesModel(BaseModel):
    model_config = MODEL_CONFIG

    pager: PagerModel
    list: list[DownloadItemModel]
    subject_id: str = Field(alias="subjectId")
    subject_type: SubjectType = Field(alias="subjectType")
    cover: Image
    subject_title: str = Field(alias="subjectTitle")
    total_size: str = Field(alias="totalSize")
    total_episode: int = Field(alias="totalEpisode")
    position: int
    resolution: ResolutionType
    collection_resolutions: list[CollectionResolutionModel] = Field(
        alias="collectionResolutions"
    )
    description: str
    genre: list[str]
    tags: list[Any]
    fav_info: Any = Field(alias="favInfo")
    release_date: str = Field(alias="releaseDate")
    country_name: str = Field(alias="countryName")
    duration_seconds: int = Field(alias="durationSeconds")

    @field_validator("genre", mode="before")
    @classmethod
    def split_genre(cls, v):
        if isinstance(v, str):
            return [g.strip() for g in v.split(",") if g.strip()]
        return v
