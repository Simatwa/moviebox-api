"""
Models for package level usage.
"""

import typing as t
from dataclasses import dataclass
from pydantic import BaseModel, HttpUrl, field_validator
from datetime import date
from uuid import UUID
from json import loads
from moviebox_api.constants import SubjectType
from moviebox_api.exceptions import ZeroSearchResultsError
from moviebox_api.constants import DownloadQualitiesType
from moviebox_api.helpers import get_file_extension


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
        return self.subjectType == SubjectType.MOVIES.value

    @property
    def is_tv_series(self) -> bool:
        """Check whether content is a tv series."""
        return self.subjectType == SubjectType.TV_SERIES.value

    @property
    def is_music(self) -> bool:
        """Check whether content is a music"""
        return self.subjectType == SubjectType.MUSIC.value


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

    @field_validator("items", mode="after")
    def validate_items(value: list[SearchResultsItem]) -> list[SearchResultsItem]:
        if not bool(value):
            raise ZeroSearchResultsError(
                "Search yielded empty results. Try a different keyword."
            )
        return value

    @property
    def first_item(self) -> SearchResultsItem:
        return self.items[0]


class BaseFileMetadata(BaseModel):

    @property
    def ext(self) -> str:
        """Media file extension such as `mp4` or `srt`"""
        return get_file_extension(self.url)


class MediaFileMetadata(BaseFileMetadata):
    id: str
    url: HttpUrl
    resolution: int
    size: int


class CaptionFileMetadata(BaseFileMetadata):
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
    limitedCode: str
    hasResource: bool

    @property
    def best_media_file(self) -> MediaFileMetadata | None:
        """Highest quality media file"""
        if bool(self.downloads):
            found = self.downloads[0]
            for media_file in self.downloads[1:]:
                if media_file.resolution > found.resolution:
                    found = media_file
            return found

    @property
    def worst_media_file(self) -> MediaFileMetadata | None:
        """Lowest quality media file"""
        if bool(self.downloads):
            found = self.downloads[0]
            for media_file in self.downloads[1:]:
                if media_file.resolution < found.resolution:
                    found = media_file
            return found

    @property
    def english_subtitle_file(self) -> CaptionFileMetadata | None:
        """English subtitle file."""
        for subtitle_file in self.captions:
            if subtitle_file.lan == "en":
                return subtitle_file

    def get_quality_downloads_map(
        self,
    ) -> t.Dict[DownloadQualitiesType, MediaFileMetadata]:
        """Maps media file quality to their equivalent media files object

        Returns:
            t.Dict[DownloadQualitiesType, MediaFileMetadata]
        """
        resolution_downloads_map = {}
        for item in self.downloads:
            resolution_downloads_map[f"{item.resolution}P"] = item
        return resolution_downloads_map

    def get_media_file_by_resolution(self, resolution: int) -> MediaFileMetadata:
        """Get specific MediaFileMetadata based on resolution.

        Args:
            resolution (int): Media file resolution e.g 480, 720, 1080 etc

        Returns:
            MediaFileMetadata: Media file matching that resolution.

        Raises:
            ValueError: Incase no media_file matched the resolution.
        """
        available_media_file_resolutions = []
        for media_file in self.downloads:
            available_media_file_resolutions.append(media_file.resolution)
            if media_file.resolution == resolution:
                return media_file
        raise ValueError(
            "No media_file matched that resolution. "
            f"Available resolutions include {available_media_file_resolutions}"
        )

    def get_language_subtitle_map(self) -> t.Dict[str, CaptionFileMetadata]:
        """Returns something like { English : CaptionFileMetadata }"""
        language_subtitle_map = {}
        for caption in self.captions:
            language_subtitle_map[caption.lanName] = caption
        return language_subtitle_map

    def get_language_short_subtitle_map(self) -> t.Dict[str, CaptionFileMetadata]:
        """Returns something like { en : CaptionFileMetadata }"""
        language_subtitle_map = {}
        for caption in self.captions:
            language_subtitle_map[caption.lan] = caption
        return language_subtitle_map

    def get_subtitle_by_language(self, language: str) -> CaptionFileMetadata | None:
        """Both of `English` and `en` will return same thing"""
        if len(language) == 2:
            return self.get_language_short_subtitle_map().get(language.lower())
        return self.get_language_subtitle_map().get(language.capitalize())


class StreamFileMetadata(BaseModel):
    format: str
    id: str
    url: HttpUrl
    resolutions: int
    size: int
    duration: int
    codecName: str


class StreamFilesMetadata(BaseModel):
    streams: list[StreamFileMetadata]
    freeNum: int
    limited: bool
    dash: list
    hls: list
    hasResource: bool

    @property
    def best_stream_file(self) -> StreamFileMetadata | None:
        """Highest quality stream file"""
        if bool(self.streams):
            found = self.streams[0]
            for stream_file in self.streams[1:]:
                if stream_file.resolutions > found.resolutions:
                    found = stream_file
            return found

    @property
    def worst_stream_file(self) -> StreamFileMetadata | None:
        """Lowest quality stream file"""
        if bool(self.streams):
            found = self.streams[0]
            for stream_file in self.streams[1:]:
                if stream_file.resolutions < found.resolutions:
                    found = stream_file
            return found
