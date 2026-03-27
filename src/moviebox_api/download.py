"""Contains functionalities for fetching and modelling downloadable files metadata
and later performing the actual download as well
"""

from pathlib import Path

import httpx
from throttlebuster import DownloadedFile, ThrottleBuster
from throttlebuster.helpers import get_filesize_string, sanitize_filename

from moviebox_api._bases import (
    BaseContentProviderAndHelper,
    BaseFileDownloaderAndHelper,
)
from moviebox_api.constants import (
    CURRENT_WORKING_DIR,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_READ_TIMEOUT_ATTEMPTS,
    DEFAULT_TASKS,
    DOWNLOAD_PART_EXTENSION,
    DOWNLOAD_QUALITIES,
    DOWNLOAD_REQUEST_HEADERS,
    DownloadMode,
    DownloadQualitiesType,
    SubjectType,
)
from moviebox_api.extractor.models.json import (
    ItemJsonDetailsModel,
    PostListItemSubjectModel,
)
from moviebox_api.helpers import assert_instance, get_absolute_url
from moviebox_api.models import (
    CaptionFileMetadata,
    DownloadableFilesMetadata,
    MediaFileMetadata,
    SearchResultsItem,
)
from moviebox_api.requests import Session

__all__ = [
    "MediaFileDownloader",
    "CaptionFileDownloader",
    "DownloadableMovieFilesDetail",
    "DownloadableTVSeriesFilesDetail",
    "resolve_media_file_to_be_downloaded",
]


def resolve_media_file_to_be_downloaded(
    quality: DownloadQualitiesType,
    downloadable_metadata: DownloadableFilesMetadata,
) -> MediaFileMetadata:
    """Gets media-file-metadata that matches the target quality

    Args:
        quality (DownloadQualitiesType): Target media quality such
        downloadable_metadata (DownloadableFilesMetadata): Downloadable files metadata

    Raises:
        RuntimeError: Incase no media file matched the target quality
        ValueError: Unexpected target media quality

    Returns:
        MediaFileMetadata: Media file details matching the target media quality
    """
    match quality:
        case "BEST":
            target_metadata = downloadable_metadata.best_media_file
        case "WORST":
            target_metadata = downloadable_metadata.worst_media_file
        case _:
            if quality in DOWNLOAD_QUALITIES:
                quality_downloads_map = downloadable_metadata.get_quality_downloads_map()
                target_metadata = quality_downloads_map.get(quality)

                if target_metadata is None:
                    raise RuntimeError(
                        f"Media file for quality {quality} does not exists. "
                        f"Try other qualities from {target_metadata.keys()}"
                    )
            else:
                raise ValueError(
                    f"Unknown media file quality passed '{quality}'. Choose from {DOWNLOAD_QUALITIES}"
                )
    return target_metadata


class BaseDownloadableFilesDetail(BaseContentProviderAndHelper):
    """Base class for fetching and modelling downloadable files detail"""

    _url = get_absolute_url(r"/wefeed-h5-bff/web/subject/download")

    def __init__(self, session: Session, item: SearchResultsItem | ItemJsonDetailsModel):
        """Constructor for `BaseDownloadableFilesDetail`

        Args:
            session (Session): MovieboxAPI request session.
            item (SearchResultsItem | ItemJsonDetailsModel): Movie/TVSeries item to handle.
        """
        assert_instance(session, Session, "session")
        assert_instance(item, (SearchResultsItem, ItemJsonDetailsModel), "item")

        self.session = session
        self._item: SearchResultsItem | PostListItemSubjectModel = (
            item.resData.postList.items[0].subject if isinstance(item, ItemJsonDetailsModel) else item
        )

    def _create_request_params(self, season: int, episode: int) -> dict:
        """Creates request parameters

        Args:
            season (int): Season number of the series.
            episde (int): Episode number of the series.
        Returns:
            t.Dict: Request params
        """
        return {
            "subjectId": self._item.subjectId,
            "se": season,
            "ep": episode,
        }

    async def get_content(self, season: int, episode: int) -> dict:
        """Performs the actual fetching of files detail.

        Args:
            season (int): Season number of the series.
            episde (int): Episode number of the series.

        Returns:
            t.Dict: File details
        """
        # Referer
        request_header = {"Referer": get_absolute_url(f"/movies/{self._item.detailPath}")}
        # Without the referer, empty response will be served.

        content = await self.session.get_with_cookies_from_api(
            url=self._url,
            params=self._create_request_params(season, episode),
            headers=request_header,
        )
        return content

    async def get_content_model(self, season: int, episode: int) -> DownloadableFilesMetadata:
        """Get modelled version of the downloadable files detail.

        Args:
            season (int): Season number of the series.
            episde (int): Episode number of the series.

        Returns:
            DownloadableFilesMetadata: Modelled file details
        """
        contents = await self.get_content(season, episode)
        return DownloadableFilesMetadata(**contents)


class DownloadableMovieFilesDetail(BaseDownloadableFilesDetail):
    """Fetches and model movie files detail"""

    async def get_content(self) -> dict:
        """Actual fetch of files detail"""
        return await super().get_content(season=0, episode=0)

    async def get_content_model(self) -> DownloadableFilesMetadata:
        """Modelled version of the files detail"""
        contents = await self.get_content()
        return DownloadableFilesMetadata(**contents)


class DownloadableTVSeriesFilesDetail(BaseDownloadableFilesDetail):
    """Fetches and model series files detail"""

    # NOTE: Already implemented by parent class - BaseDownloadableFilesDetail


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
        search_results_item: SearchResultsItem,
        media_file: MediaFileMetadata,
        season: int = 0,
        episode: int = 0,
        test: bool = False,
    ) -> tuple[str, Path]:
        """Generates filename in the format as in `self.*filename_template` and updates
        final directory for saving contents

        Args:
            search_results_item (SearchResultsItem)
            media_file (MediaFileMetadata): Movie/tv-series/music to be downloaded.
            season (int): Season number of the series.
            episde (int): Episode number of the series.

        """
        assert_instance(
            search_results_item,
            SearchResultsItem,
            "search_results_item",
        )

        assert_instance(media_file, MediaFileMetadata, "media_file")

        placeholders = dict(
            title=search_results_item.title,
            release_date=str(search_results_item.releaseDate),
            release_year=search_results_item.releaseDate.year,
            ext=media_file.ext,
            resolution=media_file.resolution,
            size_string=get_filesize_string(media_file.size),
            season=season,
            episode=episode,
        )

        filename_template: str = (
            self.series_filename_template
            if search_results_item.subjectType == SubjectType.TV_SERIES
            else self.movie_filename_template
        )

        final_dir = self.create_final_dir(
            working_dir=self.throttle_buster.dir,
            search_results_item=search_results_item,
            season=season,
            episode=episode,
            test=test,
            group=self.group_series,
        )

        return filename_template.format(**placeholders), final_dir

    async def run(
        self,
        media_file: MediaFileMetadata,
        filename: str | SearchResultsItem,
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

        if isinstance(filename, SearchResultsItem):
            filename, dir = self.generate_filename(
                search_results_item=filename, media_file=media_file, test=test, **filename_kwargs
            )

        elif self.group_series:
            raise ValueError(
                f"Value for filename should be an instance of {SearchResultsItem} "
                "when group_series is activated"
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
        """Constructor for `CaptionFileDownloader`
        Args:
            dir (Path | str, optional): Directory for downloaded files to. Defaults to CURRENT_WORKING_DIR.
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
        search_results_item: SearchResultsItem,
        caption_file: CaptionFileMetadata,
        season: int = 0,
        episode: int = 0,
        test: bool = False,
        **kwargs,
    ) -> tuple[str, Path]:
        """Generates filename in the format as in `self.*filename_template`

        Args:
            search_results_item (SearchResultsItem)
            caption_file (CaptionFileMetadata): Movie/tv-series/music caption file details.
            season (int): Season number of the series.
            episde (int): Episode number of the series.
            test (bool, optional): whether to create final directory

        Kwargs: Nothing much folk.
                It's just here so that `MediaFileDownloader.run` and `CaptionFileDownloader.run`
                will accept similar parameters in `moviebox_api.extra.movies.Auto.run` method.
        """
        assert_instance(
            search_results_item,
            SearchResultsItem,
            "search_results_item",
        )

        placeholders = dict(
            title=search_results_item.title,
            release_date=str(search_results_item.releaseDate),
            release_year=search_results_item.releaseDate.year,
            ext=caption_file.ext,
            lan=caption_file.lan,
            lanName=caption_file.lanName,
            delay=caption_file.delay,
            size_string=get_filesize_string(caption_file.size),
            season=season,
            episode=episode,
        )

        filename_template: str = (
            self.series_filename_template
            if search_results_item.subjectType == SubjectType.TV_SERIES
            else self.movie_filename_template
        )

        final_dir = self.create_final_dir(
            working_dir=self.throttle_buster.dir,
            search_results_item=search_results_item,
            season=season,
            episode=episode,
            test=test,
            group=self.group_series,
        )

        return sanitize_filename(filename_template.format(**placeholders)), final_dir

    async def run(
        self,
        caption_file: CaptionFileMetadata,
        filename: str | SearchResultsItem,
        season: int = 0,
        episode: int = 0,
        **run_kwargs,
    ) -> DownloadedFile | httpx.Response:
        """Performs the actual download, incase already downloaded then return its Path.

        Args:
            caption_file (CaptionFileMetadata): Movie/tv-series/music caption file details.
            filename (str|SearchResultsItem): Movie filename
            season (int): Season number of the series. Defaults to 0.
            episde (int): Episode number of the series. Defaults to 0.

        run_kwargs: Keyword arguments for `ThrottleBuster.run`

        Returns:
            Path | httpx.Response: Path where the caption file has been saved to or httpx Response (test).
        """

        assert_instance(caption_file, CaptionFileMetadata, "caption_file")

        dir = None

        if isinstance(filename, SearchResultsItem):
            # Lets generate filename
            filename, dir = self.generate_filename(
                search_results_item=filename,
                caption_file=caption_file,
                season=season,
                episode=episode,
                test=run_kwargs.get("test", False),
            )
        return await self.throttle_buster.run(
            url=str(caption_file.url), filename=filename, dir=dir, **run_kwargs
        )
