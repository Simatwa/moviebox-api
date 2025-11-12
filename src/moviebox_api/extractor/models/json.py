"""Models for item details extracted from json-formatted data"""

import typing as t
from datetime import date

from pydantic import BaseModel, Field, HttpUrl, field_validator

from moviebox_api.constants import SubjectType
from moviebox_api.helpers import get_absolute_url
from moviebox_api.models import (
    ContentCategorySubjectsModel,
    ContentImageModel,
)


class MetadataModel(BaseModel):
    """`.resData.metadata`"""

    description: str
    image: HttpUrl
    keyWords: list[str]
    referer: HttpUrl
    title: str
    url: HttpUrl

    @field_validator("keyWords", mode="before")
    def validate_genre(value: str) -> list[str]:
        return value.split(",")

    @field_validator("url", mode="before")
    def validate_url(value: str) -> str:
        return get_absolute_url(value) if bool(value) else value


class PubParamModel(BaseModel):
    """`.resData.pubParam`"""

    isNewUser: bool
    lang: str
    referer: HttpUrl
    uid: str
    url: HttpUrl

    @field_validator("url", mode="before")
    def validate_url(value: str) -> str:
        return get_absolute_url(value) if bool(value) else value


class SeasonsResolutionModel(BaseModel):
    """`.resData.resource.seasons.0.resolutions.0`"""

    epNum: int
    resolution: t.Literal[360, 480, 720, 1080]


class SeasonsModel(BaseModel):
    """`.resData.resource.seasons.0`"""

    allEp: str
    maxEp: int
    resolutions: list[SeasonsResolutionModel]
    se: int


class ResourceModel(BaseModel):
    """`.resData.resource`"""

    seasons: list[SeasonsModel]
    source: str
    uploadBy: str

    @property
    def total_seasons(self) -> int:
        return len(self.seasons)

    def get_season_by_number(self, number: int) -> SeasonsModel:
        for season in self.seasons:
            if season.se == number:
                return season

        raise ValueError(f"The item does not have that season number {number}")


class StarsModel(BaseModel):
    """`.resData.stars.0`"""

    avatarUrl: HttpUrl | str
    character: str
    detailPath: str
    name: str
    staffId: str
    staffType: int  # TODO: Consider using Enum

    @field_validator("avatarUrl", mode="before")
    def validate_url(value: str) -> str:
        return get_absolute_url(value) if bool(value) else value


class PagerModel(BaseModel):
    """`.resData.postList.pager.`"""

    hasMore: bool
    nextPage: str
    page: str
    perPage: int
    totalCount: int


class PostListItemStatModel(BaseModel):
    """`.resData.postList.items.0.stat`"""

    commentCount: int
    likeCount: int
    mediaViewCount: int
    shareCount: int
    viewCount: int


class PostListItemSubjectModel(BaseModel):
    """`.resData.postList.items.0.subject`"""

    countryName: str
    cover: ContentImageModel
    description: str
    detailPath: str
    detailUrl: HttpUrl | str
    dl: str | None
    duration: str
    durationSeconds: int
    genre: list[str]
    hasResource: bool
    imdbRate: float
    rate: int
    releaseDate: date
    sniffUrl: HttpUrl | str
    sourceUrl: HttpUrl | str
    subjectId: str
    subjectType: SubjectType
    title: str

    @field_validator("genre", mode="before")
    def validate_genre(value: str) -> list[str]:
        return value.split(",")

    @field_validator("detailUrl", mode="before")
    def validate_anyUrl(value: str) -> str:
        return get_absolute_url(value) if bool(value) else value

    @field_validator("sniffUrl", mode="before")
    def validate_sniffUrl(value: str) -> str:
        return get_absolute_url(value) if bool(value) else value


class PostListItemUserModel(BaseModel):
    """`.resData.postList.items.0.user`"""

    avatar: HttpUrl
    nickname: str
    userId: str
    username: str


class PostListMediaModel(BaseModel):
    """`.resData.postList.items.0.media`"""

    audio: list
    cover: ContentImageModel | str | None
    firstFrame: ContentImageModel | str | None
    image: list[ContentImageModel]
    mediaType: str
    video: list


class PostListItemGroupModel(BaseModel):
    """`.resData.postList.items.0.group`"""

    avatar: HttpUrl
    groupId: str
    name: str
    postCount: int
    userCount: int


class PostListItemModel(BaseModel):
    """`.resData.postList.items.0`"""

    commentList: list
    content: str
    cover: ContentImageModel
    createdAt: str
    group: PostListItemGroupModel | None
    groupId: str
    isSubjectRate: bool
    link: str | dict | None
    media: PostListMediaModel | None
    mediaType: str
    poiName: str
    postId: str
    stat: PostListItemStatModel
    status: int
    subject: PostListItemSubjectModel
    subjectId: str
    subjectRate: int
    title: str
    updatedAt: str
    user: PostListItemUserModel | None
    userId: str


class PostListModel(BaseModel):
    """`.resData.postList.`"""

    items: list[PostListItemModel]
    pager: PagerModel


class TrailerVideoAddressModel(BaseModel):
    """`.resData.subject.trailer.videoAddress`"""

    bitrate: int
    definition: str
    duration: int
    fps: int
    height: int
    size: int
    type: int
    url: HttpUrl
    videoId: str
    width: int


class SubjectTrailerModel(BaseModel):
    """`.resData.subject.trailer`"""

    cover: ContentImageModel
    videoAddress: TrailerVideoAddressModel


class SubjectModel(ContentCategorySubjectsModel):
    """`.resData.subject`"""

    title: str
    trailer: SubjectTrailerModel | None


class ResDataModel(BaseModel):
    """`.resData`"""

    metadata: MetadataModel
    postList: PostListModel
    pubParam: PubParamModel
    referer: HttpUrl
    resource: ResourceModel
    stars: list[StarsModel]
    subject: SubjectModel
    url: HttpUrl

    @field_validator("url", mode="before")
    def validate_url(value: str) -> str:
        return get_absolute_url(value) if bool(value) else value


class ItemJsonDetailsModel(BaseModel):
    """Whole extracted item details from json-formatted data"""

    nuxt_i18n_meta: dict = Field(alias="nuxt-i18n-meta")
    resData: ResDataModel
    utmSource: str
    showNotFound: bool
    # midForYou: list
    midReviewsList: list[PostListItemModel]
    pcShowSliderNav: bool
    detailShowSliderNav: bool
    QRCode: str
    activeSidebar: str
    playSourceTabType: int
