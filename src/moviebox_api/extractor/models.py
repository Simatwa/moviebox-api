"""Pydantic models of extracted contents"""

import typing as t
from datetime import date
from pydantic import BaseModel, Field, HttpUrl, field_validator
from moviebox_api.constants import SubjectType
from moviebox_api.models import ContentImageModel, ContentCategorySubjectsModel


class MetadataModel(BaseModel):
    """`resData.metadata`"""

    description: str
    image: HttpUrl
    keywords: str
    referer: HttpUrl
    title: str
    url: str


class PubParamModel(BaseModel):
    """`resData.pubParam`"""

    isNewUser: bool
    lang: str
    referer: HttpUrl
    uid: str
    url: str


class SeasonsResolutionModel(BaseModel):
    """`resData.resource.seasons.0.resolutions.0`"""

    epNum: int
    resolution: t.Literal[360, 480, 720, 1080]


class SeasonsModel(BaseModel):
    """`resData.resource.seasons.0`"""

    allEp: str
    maxEp: int
    resolutions: list[SeasonsResolutionModel]
    se: int


class ResourceModel(BaseModel):
    """`resData.resource`"""

    seasons: list[SeasonsModel]
    source: str
    uploadBy: str


class StarsModel(BaseModel):
    """`resData.stars.0`"""

    avatarUrl: HttpUrl
    character: str
    detailPath: str
    name: str
    staffId: str
    staffType: int  # TODO: Consider using Enum


class PagerModel(BaseModel):
    """`resData.postList.pager.`"""

    hasMore: bool
    nextPage: str
    page: str
    perPage: int
    totalCount: int


class PostListItemStatModel(BaseModel):
    """`resData.postList.0.stat`"""

    commentCount: int
    likeCount: int
    mediaViewCount: int
    shareCount: int
    viewCount: int


class PostListItemSubjectModel(BaseModel):
    """`resData.postList.0.subject`"""

    countryName: str
    cover: ContentImageModel
    description: str
    detailPath: str
    detailUrl: str
    dl: str | None
    duration: str
    durationSeconds: int
    genre: list[str]
    hasResource: bool
    imdbRate: float
    rate: int
    releaseDate: date
    sniffUrl: str
    sourceurl: HttpUrl
    subjectId: str
    subjectType: SubjectType
    title: str

    @field_validator("genre", mode="before")
    def validate_genre(value: str) -> list[str]:
        return value.split(",")


class PostListItemUserModel(BaseModel):
    """`resData.postList.0.user`"""

    avatar: HttpUrl
    nickname: str
    userId: str
    username: str


class PostListItemModel(BaseModel):
    """`resData.postList.0`"""

    comment: list
    content: str
    cover: ContentImageModel
    createdAt: str
    group: str | None
    groupId: str
    isSubjectRate: bool
    link: str | None
    media: str | None
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
    user: PostListItemUserModel
    userId: str


class PostListModel(BaseModel):
    """`resData.postList.`"""

    items: list[PostListItemModel]
    pager: PagerModel


class TrailerVideoAddressModel(BaseModel):
    """`resData.subject.trailer.videoAddress`"""

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
    """`resData.subject.trailer`"""

    cover: ContentImageModel
    videoAddress: TrailerVideoAddressModel


class SubjectModel(ContentCategorySubjectsModel):
    """`resData.subject`"""

    title: str
    trailer: SubjectTrailerModel


class ResDataModel(BaseModel):
    """`resData`"""

    metadata: MetadataModel
    url: HttpUrl
    postList: PostListModel
    pubParam: PubParamModel
    referer: HttpUrl
    resource: ResourceModel
    stars: list[StarsModel]
    subject: SubjectModel
    url: HttpUrl


class ItemDetailsModel(BaseModel):
    """Complete extracted item details

    - Houses all the other models
    """

    nuxt_i18n_meta: dict = Field(alias="nuxt-i18n-meta")
    resData: ResDataModel
    utmSource: str
    showNotFound: bool
    midForYou: list
    midReviewsList: list[PostListItemModel]
    pcShowSliderNav: bool
    detailShowSliderNav: bool
    QRCode: str
    activeSidebar: str
    playSourceTabType: int
