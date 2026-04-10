from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, field_validator

from moviebox_api.v3.constants import (
    CustomResolutionType,
    ResolutionType,
    SubjectType,
)
from moviebox_api.v3.exceptions import ZeroMediaFileError
from moviebox_api.v3.models.common import DEFAULT_DATETIME, MODEL_CONFIG
from moviebox_api.v3.models.search import Image, PagerModel


class MediaFileMetadata(BaseModel):
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
    resolution: int
    codec_name: str = Field(alias="codecName")
    duration: int
    require_member_type: int = Field(alias="requireMemberType")
    member_icon: str = Field(alias="memberIcon")

    @property
    def url(self):
        return self.resource_link

    @property
    def season(self):
        return self.se

    @property
    def episode(self):
        return self.se


class CollectionResolutionModel(BaseModel):
    model_config = MODEL_CONFIG

    resolution: ResolutionType
    average_size: str = Field(alias="averageSize")
    ep_num: int = Field(alias="epNum")
    require_member_type: int = Field(alias="requireMemberType")
    member_icon: str = Field(alias="memberIcon")


class RootDownloadableFilesDetailModel(BaseModel):
    model_config = MODEL_CONFIG

    pager: PagerModel
    list: list[MediaFileMetadata]
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
    release_date: datetime = Field(alias="releaseDate")
    country_name: str = Field(alias="countryName")
    duration_seconds: int = Field(alias="durationSeconds")

    @property
    def title(self) -> str:
        return self.subject_title

    @field_validator("genre", mode="before")
    @classmethod
    def split_genre(cls, v):
        if isinstance(v, str):
            return [g.strip() for g in v.split(",") if g.strip()]
        return v

    @field_validator("release_date", mode="before")
    def validate_release_date(value: str):
        if not bool(value):
            return DEFAULT_DATETIME

        try:
            return datetime.strptime(value, "%Y-%m-%d")

        except Exception:
            if value.isdigit():
                return datetime(year=int(value), month=1, day=1)

            return DEFAULT_DATETIME

    def _check_list(self) -> bool:
        """Checks whether there are downloadable media file.

        Raises:
            ZeroMediaFileError: Incase the downloads list is empty

        Returns:
            bool: Downloadable media file(s) exist.
        """
        if bool(self.list):
            if self.subject_type is SubjectType.TV_SERIES:
                raise ValueError(
                    "media_file shortcuts are only reserved for non-series "
                    "downloadable files detail such as movies, music etc"
                )
            return True

        raise ZeroMediaFileError(
            "There are no downloadable mediafiles for the targeted item"
        )

    @property
    def best_media_file(self) -> MediaFileMetadata:
        """Highest quality media file"""
        self._check_list()
        found = self.list[0]
        for media_file in self.list[1:]:
            if media_file.resolution > found.resolution:
                found = media_file

        return found

    @property
    def worst_media_file(self) -> MediaFileMetadata:
        """Lowest quality media file"""
        self._check_list()
        found = self.list[0]
        for media_file in self.list[1:]:
            if media_file.resolution < found.resolution:
                found = media_file

        return found

    def get_quality_downloads_map(
        self,
    ) -> dict[CustomResolutionType, MediaFileMetadata]:
        """Maps media file qualities to their equivalent media file objects

        Returns:
            dict[CustomResolutionType, MediaFileMetadata]
        """
        resolution_list_map = {}
        for item in self.list:
            resolution_list_map[
                CustomResolutionType(f"{item.resolution}P")
            ] = item

        return resolution_list_map

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
        for media_file in self.list:
            available_media_file_resolutions.append(media_file.resolution)
            if media_file.resolution == resolution:
                return media_file

        raise ValueError(
            "No media_file matched that resolution. Available resolutions "
            f"include {available_media_file_resolutions}"
        )
