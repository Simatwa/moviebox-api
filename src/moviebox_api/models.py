""" 
Models for package level usage.
"""

from dataclasses import dataclass
from pydantic import BaseModel, HttpUrl, field_validator
from datetime import date
from uuid import UUID
from json import loads
from moviebox_api.utils import SubjectType


@dataclass(frozen=True)
class MovieboxAppInfo:
    """This data is fetched when requesting for cookies,
    so I just find it important that I expose it in the package
    """

    channelType: str
    pkgName: str
    url: str
    versionCode: str
    versionName: str


class ContentImageModel(BaseModel):
    """Model for content image"""

    url: HttpUrl
    width: int
    height: int
    size: int
    format: str
    thumbnail: str
    blurHash: str
    gif: str | None = None
    avgHueLight: str
    avgHueDark: str
    id: str


class ContentSubjectModel(BaseModel):
    subjectId: str
    subjectType: SubjectType
    title: str
    description: str
    releaseDate: date
    duration: int
    genre: str
    cover: ContentImageModel
    countryName: str
    imdbRatingValue: float
    # subtitles : str
    # ops : {rid: uuid, trace_id: str}
    # hasResource :bool
    trailer: str | None = None
    detailPath: str
    stafflist: list | None = None
    appointmentCnt: int
    appointmentDate: str
    corner: str
    # imdbRatingCount: int


class ContentModel(BaseModel):
    """Model for a particular movie or tv series"""

    id: str
    title: str
    image: ContentImageModel
    url: HttpUrl
    subjectId: str
    subjectType: int
    subject: ContentSubjectModel | None = None

    @property
    def is_movie(self) -> bool:
        """Check whether content is a movie._"""
        return self.subjectType == 1

    @property
    def is_tv_series(self) -> bool:
        """Check whether content is a tv series."""
        return self.subjectType == 2


class PlatformsModel(BaseModel):
    name: str
    uploadBy: str


class ContentCategoryBannerModel(BaseModel):
    items: list[ContentModel]  # list of series/movies


class ContentCategoryModel(BaseModel):
    # named: OperatingList in server response
    type: str
    position: int
    title: str
    subjects: list
    banner: ContentCategoryBannerModel | None = None
    opId: str
    url: str
    livelist: list | None = None


class HomepageContentModel(BaseModel):
    """Main model for home contents
    - Movies/series available under path operatingList[0].banner.items
    """

    topPickList: list
    homeList: list
    url: str
    referer: str
    allPlatform: list
    banner: str | None = None
    live: str | None = None
    platformList: list[PlatformsModel]
    shareParam: str | None = None
    operatingList: list[ContentCategoryModel]

    @property
    def contents(self) -> list[ContentModel]:
        """Both movies and tv series"""
        cached_contents = []
        for operating in self.operatingList:
            if operating.banner is not None:
                cached_contents.extend(operating.banner.items)
        return cached_contents


class OPS(BaseModel):
    """A value in specific result info"""

    rid: UUID
    trace_id: str


class SearchResultsItem(ContentSubjectModel):
    """Specific result info"""

    subtitles: list[str]
    ops: OPS
    hasResource: bool
    imdbRatingCount: int

    @field_validator("ops", mode="before")
    def validate_ops(value: str) -> dict:
        return loads(value)

    @field_validator("subtitles", mode="before")
    def validate_subtitles(value: str) -> list[str]:
        return value.split(",")


class SearchResultsPager(BaseModel):
    """Search pagination info"""

    hasMore: bool
    nextPage: int
    page: int
    perPage: int
    totalCount: int


class SearchResults(BaseModel):
    """Whole search results"""

    pager: SearchResultsPager
    items: list[SearchResultsItem]


class MediaFileMetadata(BaseModel):
    id: str
    url: HttpUrl
    resolution: int
    size: int


class CaptionFileMetadata(BaseModel):
    id: str
    lan: str
    lanName: str
    url: HttpUrl
    size: int
    delay: int


class DownloadableFilesMetadata(BaseModel):
    downloads: list[MediaFileMetadata]
    captions: list[CaptionFileMetadata]
    limited: bool
    limitedCode: int
    hasResource: bool
