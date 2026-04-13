"""Makes local copy of remote files"""

from pathlib import Path

import httpx
from throttlebuster import DownloadedFile, ThrottleBuster
from throttlebuster.helpers import get_filesize_string, sanitize_filename

from moviebox_api.v3._bases import (
    BaseFileDownloaderAndHelper,
)
from moviebox_api.v3.constants import (
    CURRENT_WORKING_DIR,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_READ_TIMEOUT_ATTEMPTS,
    DEFAULT_TASKS,
    DOWNLOAD_PART_EXTENSION,
    DOWNLOAD_REQUEST_HEADERS,
    CustomResolutionType,
    DownloadMode,
    SubjectType,
)
from moviebox_api.v3.helpers import assert_instance, get_file_extension
from moviebox_api.v3.models.downloadables import (
    MediaFileMetadata,
    RootDownloadableFilesDetailModel,
)

__all__ = [
    "MediaFileDownloader",
    "CaptionFileDownloader",
    "resolve_media_file_to_be_downloaded",
]


def resolve_media_file_to_be_downloaded(
    resolution: CustomResolutionType,
    downloadable_files_detail: RootDownloadableFilesDetailModel,
) -> MediaFileMetadata:
    """Gets media-file-metadata that matches the target quality. Only for
        movie and other non-series items such as music etc

    Args:
        quality (CustomResolutionType): Target media resolution
        downloadable_metadata (DownloadableFilesMetadata): Downloadable files
            metadata

    Raises:
        RuntimeError: Incase no media file matched the target quality
        ValueError: Unexpected target media quality

    Returns:
        MediaFileMetadata: Media file details matching the target media quality
    """
    assert_instance(resolution, CustomResolutionType, "resolution")
    if downloadable_files_detail.subject_type is SubjectType.TV_SERIES:
        raise ValueError(
            "Can only process items which falls under non-series "
            f"subject types such as {SubjectType.MOVIES}, {SubjectType.MUSIC} etc"
            f" NOT {downloadable_files_detail.subject_type}"
        )

    match resolution:
        case CustomResolutionType.BEST:
            target_metadata = downloadable_files_detail.best_media_file

        case CustomResolutionType.WORST:
            target_metadata = downloadable_files_detail.worst_media_file

        case _:
            quality_downloads_map = (
                downloadable_files_detail.get_quality_downloads_map()
            )
            target_metadata = quality_downloads_map.get(resolution)

            if target_metadata is None:
                raise RuntimeError(
                    f"Media file for quality {resolution} does not exists. "
                    f"Try other qualities from {quality_downloads_map.keys()}"
                )

    return target_metadata


class MediaFileDownloader(BaseFileDownloaderAndHelper):
    """Download movie and tv-series files"""

    request_headers = DOWNLOAD_REQUEST_HEADERS
    request_cookies = {}

    movie_filename_template = "{title} ({release_year}).{ext}"
    series_filename_template = "{title} S{season}E{episode}.{ext}"

    # Should have been named episode_filename_template but for consistency
    # with the subject-types {movie, tv-series, music} it's better as it is
    possible_filename_placeholders = (
        "{title}",
        "{release_year}",
        "{release_date}",
        "{resolution}",
        "{ext}",
        "{size_string}",
        "{season}",
        "{episode}",
        "{episode_title}",
        "{duration}",
        "{codec_name}",
    )

    def __init__(
        self,
        dir: Path | str = CURRENT_WORKING_DIR,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        tasks: int = DEFAULT_TASKS,
        part_dir: Path | str = CURRENT_WORKING_DIR,
        part_extension: str = DOWNLOAD_PART_EXTENSION,
        merge_buffer_size: int | None = None,
        group_series: bool = False,
        **httpx_kwargs,
    ):
        """Constructor for `MediaFileDownloader`

        Args:
            dir (Path | str, optional): Directory for saving downloaded files to. Defaults to CURRENT_WORKING_DIR.
            chunk_size (int, optional): Streaming download chunk size in kilobytes. Defaults to DEFAULT_CHUNK_SIZE.
            tasks (int, optional): Number of tasks to carry out the download. Defaults to DEFAULT_TASKS.
            part_dir (Path | str, optional): Directory for temporarily saving downloaded file-parts to. Defaults to CURRENT_WORKING_DIR.
            part_extension (str, optional): Filename extension for download parts. Defaults to DOWNLOAD_PART_EXTENSION.
            merge_buffer_size (int|None, optional). Buffer size for merging the separated files in kilobytes. Defaults to chunk_size.
            group_series(bool, optional): Create directory for a series & group episodes based on season number. Defaults to False.

        httpx_kwargs : Keyword arguments for `httpx.AsyncClient`
        """  # noqa: E501

        httpx_kwargs.setdefault("cookies", self.request_cookies)
        self.group_series = group_series

        self.throttle_buster = ThrottleBuster(
            dir=dir,
            chunk_size=chunk_size,
            tasks=tasks,
            part_dir=part_dir,
            part_extension=part_extension,
            merge_buffer_size=merge_buffer_size,
            request_headers=self.request_headers,
            **httpx_kwargs,
        )

    def generate_filename(
        self,
        media_file: MediaFileMetadata,
        downloadable_files_detail: RootDownloadableFilesDetailModel,
        test: bool = False,
    ) -> tuple[str, Path]:
        """Generates filename in the format as in `self.*filename_template` and
        updates final directory for saving contents

        """
        assert_instance(
            downloadable_files_detail,
            RootDownloadableFilesDetailModel,
            "downloadable_files_detail",
        )
        assert_instance(media_file, MediaFileMetadata, "media_file")

        placeholders = dict(
            title=downloadable_files_detail.title,
            release_date=str(downloadable_files_detail.release_date),
            release_year=downloadable_files_detail.release_date.year,
            ext=get_file_extension(media_file.resource_link),
            resolution=media_file.resolution,
            size_string=get_filesize_string(media_file.size),
            season=media_file.season,
            episode=media_file.episode,
            episode_tile=media_file.title,
            duration=media_file.duration,
            codec_name=media_file.codec_name,
        )

        filename_template: str = (
            self.series_filename_template
            if downloadable_files_detail.subject_type == SubjectType.TV_SERIES
            else self.movie_filename_template
        )

        final_dir = self.create_final_dir(
            working_dir=self.throttle_buster.dir,
            downloadable_files_detail=downloadable_files_detail,
            season=media_file.season,
            episode=media_file.episode,
            test=test,
            group=self.group_series,
        )

        return filename_template.format(**placeholders), final_dir

    async def run(
        self,
        media_file: MediaFileMetadata,
        filename: str | RootDownloadableFilesDetailModel,
        progress_hook: callable = None,
        mode: DownloadMode = DownloadMode.AUTO,
        disable_progress_bar: bool = None,
        file_size: int = None,
        keep_parts: bool = False,
        timeout_retry_attempts: int = DEFAULT_READ_TIMEOUT_ATTEMPTS,
        colour: str = "cyan",
        simple: bool = False,
        test: bool = False,
        leave: bool = True,
        ascii: bool = False,
        **filename_kwargs,
    ) -> DownloadedFile | httpx.Response:
        """Performs the actual download.

        Args:
            media_file (MediaFileMetadata): Movie/tv-series/music to be downloaded.
            filename (str, optional): Filename for the downloaded content. Defaults to None.
            progress_hook (callable, optional): Function to call with the download progress information. Defaults to None.
            mode (DownloadMode, optional): Whether to start or resume incomplete download. Defaults DownloadMode.AUTO.
            disable_progress_bar (bool, optional): Do not show progress_bar. Defaults to None (decide based on progress_hook).
            file_size (int, optional): Size of the file to be downloaded. Defaults to None.
            keep_parts (bool, optional): Whether to retain the separate download parts. Defaults to False.
            timeout_retry_attempts (int, optional): Number of times to retry download upon read request timing out. Defaults to DEFAULT_READ_TIMEOUT_ATTEMPTS.
            leave (bool, optional): Keep all leaves of the progressbar. Defaults to True.
            colour (str, optional): Progress bar display color. Defaults to "cyan".
            simple (bool, optional): Show percentage and bar only in progressbar. Deafults to False.
            test (bool, optional): Just test if download is possible but do not actually download. Defaults to False.
            ascii (bool, optional): Use unicode (smooth blocks) to fill the progress-bar meter. Defaults to False.

        filename_kwargs: Keyworded arguments for generating filename incase instance of filename is SearchResultsItem.

        Returns:
            DownloadedFile | httpx.Response: Downloaded file details or httpx stream response (test).
        """  # noqa: E501

        assert_instance(media_file, MediaFileMetadata, "media_file")

        dir = None

        if isinstance(filename, RootDownloadableFilesDetailModel):
            filename, dir = self.generate_filename(
                media_file=media_file,
                downloadable_files_detail=filename,
                test=test,
                **filename_kwargs,
            )

        elif self.group_series:
            raise ValueError(
                "Value for filename should be an instance of "
                f"{RootDownloadableFilesDetailModel}"
                " when group_series is activated"
            )

        return await self.throttle_buster.run(
            url=str(media_file.url),
            filename=filename,
            progress_hook=progress_hook,
            mode=mode,
            disable_progress_bar=disable_progress_bar,
            file_size=file_size,
            keep_parts=keep_parts,
            timeout_retry_attempts=timeout_retry_attempts,
            colour=colour,
            simple=simple,
            test=test,
            leave=leave,
            ascii=ascii,
            dir=dir,
        )


# TODO: Complete this"""
class CaptionFileDownloader(BaseFileDownloaderAndHelper):
    """Creates a local copy of a remote subtitle/caption file"""

    request_headers = DOWNLOAD_REQUEST_HEADERS
    request_cookies = {}
    movie_filename_template = "{title} ({release_year}).{lan}.{ext}"
    series_filename_template = "{title} S{season}E{episode}.{lan}.{ext}"
    possible_filename_placeholders = (
        "{title}",
        "{release_year}",
        "{release_date}",
        "{ext}",
        "{size_string}",
        "{id}",
        "{lan}",
        "{lanName}",
        "{delay}",
        "{season}",
        "{episode}",
    )
