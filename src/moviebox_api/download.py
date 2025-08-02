"""Contains functionalities for fetching and model downloadable files metadata
and later performing the actual download as well
"""

import httpx

from os import getcwd, path
from pathlib import Path

from moviebox_api import logger

from tqdm import tqdm

import typing as t

from moviebox_api._bases import BaseContentProvider
from moviebox_api.models import (
    SearchResultsItem,
    DownloadableFilesMetadata,
    MediaFileMetadata,
    CaptionFileMetadata,
)

from moviebox_api.requests import Session

from moviebox_api.helpers import (
    assert_instance,
    get_absolute_url,
    get_filesize_string,
    sanitize_filename,
)

from moviebox_api.constants import (
    SubjectType,
    DOWNLOAD_REQUEST_HEADERS,
    downloadQualitiesType,
    DOWNLOAD_QUALITIES,
    DownloadMode,
)
from moviebox_api.exceptions import DownloadCompletedError


# TODO: Make tqdm required dependency

__all__ = [
    "MediaFileDownloader",
    "CaptionFileDownloader",
    "DownloadableMovieFilesDetail",
    "DownloadableSeriesFilesDetail",
    "resolve_media_file_to_be_downloaded",
]


def resolve_media_file_to_be_downloaded(
    quality: downloadQualitiesType, downloadable_metadata: DownloadableFilesMetadata
) -> DownloadableFilesMetadata:
    match quality:
        case "BEST":
            target_metadata = downloadable_metadata.best_media_file
        case "WORST":
            target_metadata = downloadable_metadata.worst_media_file
        case "_":
            if quality in DOWNLOAD_QUALITIES:
                quality_downloads_map = (
                    downloadable_metadata.get_quality_downloads_map()
                )
                target_metadata = quality_downloads_map.get(quality)
                if target_metadata is None:
                    raise ValueError(
                        f"Media file for quality {quality} does not exists. "
                        f"Try other qualities from {target_metadata.keys()}"
                    )
            else:
                raise ValueError(
                    f"Unknown media file quality expected {quality}. "
                    f"Choose from {DOWNLOAD_QUALITIES}"
                )
    return target_metadata


class BaseDownloadableFilesDetail(BaseContentProvider):
    """Base class for fetching and modelling downloadable files details"""

    _url = get_absolute_url(r"/wefeed-h5-bff/web/subject/download")

    def __init__(self, session: Session, item: SearchResultsItem):
        """Constructor for `BaseDownloadableFilesDetail`

        Args:
            session (Session): MovieboxAPI request session.
            item (SearchResultsItem): Movie item to handle.
        """
        assert_instance(session, Session, "session")
        assert_instance(item, SearchResultsItem, "item")
        self.session = session
        self._item = item

    def _create_request_params(self, season: int, episode: int) -> t.Dict:
        """Creates request parameters

        Args:
            season (int): Season number of the series.
            episde (int): Episode number of the series.
        Returns:
            t.Dict: Request params
        """
        return {"subjectId": self._item.subjectId, "se": season, "ep": episode}

    async def get_content(self, season: int, episode: int) -> t.Dict:
        """Performs the actual fetching of files detail.

        Args:
            season (int): Season number of the series.
            episde (int): Episode number of the series.

        Returns:
            t.Dict: File details
        """
        # Referer
        request_header = {
            "Referer": get_absolute_url(f"/movies/{self._item.detailPath}")
        }
        # Without the referer, empty response will be served.

        content = await self.session.get_with_cookies_from_api(
            url=self._url,
            params=self._create_request_params(season, episode),
            headers=request_header,
        )
        return content

    async def get_modelled_content(
        self, season: int, episode: int
    ) -> DownloadableFilesMetadata:
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

    async def get_content(self):
        return await super().get_content(season=0, episode=0)

    async def get_modelled_content(self):
        contents = await self.get_content()
        return DownloadableFilesMetadata(**contents)


class DownloadableSeriesFilesDetail(BaseDownloadableFilesDetail):
    """Fetches and model series files detail"""

    # NOTE: Already implemented by parent class - BaseDownloadableFilesDetail


class MediaFileDownloader:
    """Download movie and tv-series files"""

    request_headers = DOWNLOAD_REQUEST_HEADERS
    request_cookies = {}
    movie_filename_template = "%(title)s (%(release_year)d) - %(resolution)dP.%(ext)s"
    series_filename_template = (
        "%(title)s (%(release_year)d) S%(season)dE%(episode)d - %(resolution)dP.%(ext)s"
    )
    possible_filename_placeholders = (
        "%(title)s",
        "%(release_year)d",
        "%(release_date)s",
        "%(resolution)d",
        "%(ext)s",
        "%(size_string)s",
        "%(season)d",
        "%(episode)d",
    )

    def __init__(self, media_file: MediaFileMetadata):
        """Constructor for `MediaFileDownloader`
        Args:
            session (Session): MovieboxAPI request session.
            media_file (MediaFileMetadata): Movie/tv-series/music to be downloaded.
        """
        assert_instance(media_file, MediaFileMetadata, "media_file")
        self._media_file = media_file
        self.session = httpx.AsyncClient(
            headers=self.request_headers, cookies=self.request_cookies
        )
        """Httpx client session for downloading the file"""

    def generate_filename(
        self,
        search_results_item: SearchResultsItem,
        season: int = 0,
        episode: int = 0,
    ) -> str:
        """Generates filename in the format as in `self.*filename_template`

        Args:
            search_results_item (SearchResultsItem)
            season (int): Season number of the series.
            episde (int): Episode number of the series.

        Returns:
            str: Generated filename
        """
        assert_instance(search_results_item, SearchResultsItem, "search_results_item")
        placeholders = dict(
            title=search_results_item.title,
            release_date=str(search_results_item.releaseDate),
            release_year=search_results_item.releaseDate.year,
            ext=self._media_file.ext,
            resolution=self._media_file.resolution,
            size_string=get_filesize_string(self._media_file.size),
            season=season,
            episode=episode,
        )
        filename_template = (
            self.series_filename_template
            if search_results_item.subjectType == SubjectType.TV_SERIES
            else self.movie_filename_template
        )
        return sanitize_filename(filename_template % placeholders)

    async def run(
        self,
        filename: str | SearchResultsItem,
        dir: str = getcwd(),
        progress_bar=True,
        chunk_size: int = 512,
        mode: DownloadMode = DownloadMode.AUTO,
        colour: str = "cyan",
        simple: bool = False,
        test: bool = False,
        leave: bool = True,
        ascii: bool = False,
        suppress_complete_error: bool = False,
        **kwargs,
    ) -> Path | httpx.Response:
        """Performs the actual download.

        Args:
            filename (str|SearchResultsItem): Movie filename
            dir (str, optional): Directory for saving the contents Defaults to current directory.
            progress_bar (bool, optional): Display download progress bar. Defaults to True.
            chunk_size (int, optional): Chunk_size for downloading files in KB. Defaults to 512.
            mode (DownloadMode, DownloadMode.AUTO): Whether to start fresh download, resume or auto decide the download. Defaults to Auto.
            leave (bool, optional): Keep all leaves of the progressbar. Defaults to True.
            colour (str, optional): Progress bar display color. Defaults to "cyan".
            simple (bool, optional): Show percentage and bar only in progressbar. Deafults to False.
            test (bool, optional): Just test if download is possible but do not actually download. Defaults to False.
            ascii (bool, optional): Use unicode (smooth blocks) to fill the progress-bar meter. Defaults to False.
            suppress_complete_error (bool, optional): Do not raise error when trying to resume a complete download. Defaults to False.
            **kwargs: Keyworded arguments for generating filename incase instance of filename is SearchResultsItem.

        Raises:
            FileExistsError:  Incase of `resume=True` but the download was complete

        Returns:
            str|httpx.Response: Path where the media file has been saved to or httpx Response (test).
        """
        assert_instance(mode, DownloadMode, "mode")
        current_downloaded_size = 0
        current_downloaded_size_in_mb = 0
        if isinstance(filename, SearchResultsItem):
            # Lets generate filename
            filename = self.generate_filename(filename, **kwargs)

        save_to = Path(dir) / filename

        match mode:

            case DownloadMode.RESUME:
                resume = True

            case DownloadMode.START:
                resume = False

            case DownloadMode.AUTO:
                # AUTO
                resume = save_to.exists()

        def pop_range_in_session_headers():
            if self.session.headers.get("Range"):
                self.session.headers.pop("Range")

        if resume:
            logger.debug("Download set to resume")
            if not path.exists(save_to):
                raise FileNotFoundError(f"File not found in path - '{save_to}'")
            current_downloaded_size = path.getsize(save_to)
            # Set the headers to resume download from the last byte
            self.session.headers.update({"Range": f"bytes={current_downloaded_size}-"})
            current_downloaded_size_in_mb = current_downloaded_size / 1000000
        else:
            logger.debug("Download set to start afresh")

        size_in_bytes = self._media_file.size

        if resume:
            if size_in_bytes == current_downloaded_size:
                if suppress_complete_error:
                    logger.info(
                        f"Download already completed for the file in path - {save_to}"
                    )
                    return save_to
                raise DownloadCompletedError(
                    save_to, f"Download completed for the file in path - '{save_to}'"
                )

        size_in_mb = (size_in_bytes / 1_000_000) + current_downloaded_size_in_mb
        size_with_unit = get_filesize_string(self._media_file.size)
        chunk_size_in_bytes = chunk_size * 1_000

        saving_mode = "ab" if resume else "wb"
        logger.info(
            f"Downloading media file ({size_with_unit}, resume - {resume}). "
            f"Writing to ({save_to})"
        )
        if progress_bar:
            async with self.session.stream(
                "GET", str(self._media_file.url)
            ) as response:
                response.raise_for_status()
                if test:
                    logger.info(
                        f"Download test passed successfully {response.__repr__}"
                    )
                    return response
                with open(save_to, saving_mode) as fh:
                    p_bar = tqdm(
                        desc=f"Downloading {'' if simple else f'[{filename}]'}",
                        total=round(size_in_mb, 1),
                        unit="Mb",
                        # unit_scale=True,
                        colour=colour,
                        leave=leave,
                        initial=current_downloaded_size_in_mb,
                        ascii=ascii,
                        bar_format=(
                            "{l_bar}{bar} | %(size)s" % (dict(size=size_with_unit))
                            if simple
                            else "{l_bar}{bar}{r_bar}"
                        ),
                    )
                    async for chunk in response.aiter_bytes(chunk_size_in_bytes):
                        fh.write(chunk)
                        p_bar.update(round(chunk_size_in_bytes / 1_000_000, 1))
            pop_range_in_session_headers()
            logger.info(f"{filename} - {size_with_unit} ✅")
            return save_to
        else:
            logger.debug(f"Movie file info {self._media_file}")
            async with self.session.stream(
                "GET", str(self._media_file.url)
            ) as response:
                response.raise_for_status()
                if test:
                    logger.info(
                        f"Download test passed successfully {response.__repr__}"
                    )
                    return response
                with open(save_to, saving_mode) as fh:
                    async for chunk in response.aiter_bytes(chunk_size_in_bytes):
                        fh.write(chunk)
            pop_range_in_session_headers()
            logger.info(f"{filename} - {size_with_unit} ✅")
            pop_range_in_session_headers()
            return save_to


class CaptionFileDownloader:
    """Creates a local copy of a remote subtitle/caption file"""

    request_headers = DOWNLOAD_REQUEST_HEADERS
    request_cookies = {}
    movie_filename_template = (
        "%(title)s (%(release_year)d) - %(lanName)s.%(ext)s"
        # "%(title)s (%(release_year)d) - %(lanName)s [delay - %(delay)d].%(ext)s"
    )
    series_filename_template = (
        "%(title)s (%(release_year)d) S%(season)dE%(episode)d - %(lanName)s.%(ext)s"
    )
    possible_filename_placeholders = (
        "%(title)s",
        "%(release_year)d",
        "%(release_date)s",
        "%(ext)s",
        "%(size_string)s",
        "%(id)s",
        "%(lan)s",
        "%(lanName)s",
        "%(delay)d",
        "%(season)d",
        "%(episode)d",
    )

    def __init__(self, caption_file: CaptionFileMetadata):
        """Constructor for `CaptionFileDownloader`
        Args:
            session (Session): MovieboxAPI request session.
            caption_file (CaptionFileMetadata): Movie/tv-series/music to be downloaded.
        """
        assert_instance(caption_file, CaptionFileMetadata, "caption_file")
        self._caption_file = caption_file
        self.session = httpx.AsyncClient(
            headers=self.request_headers, cookies=self.request_cookies
        )
        """Httpx client session for downloading the file"""

    def generate_filename(
        self,
        search_results_item: SearchResultsItem,
        season: int = 0,
        episode: int = 0,
        **kwargs,
    ) -> str:
        """Generates filename in the format as in `self.filename_template`

        Args:
            search_results_item (SearchResultsItem)
            season (int): Season number of the series.
            episde (int): Episode number of the series.

        Kwargs: Nothing much folk.
                It's just here so that `MediaFileDownloader.run` and `CaptionFileDownloader.run`
                will accept similar parameters in `moviebox_api.extra.movies.Auto.run` method.

        Returns:
            str: Generated filename
        """
        assert_instance(search_results_item, SearchResultsItem, "search_results_item")
        placeholders = dict(
            title=search_results_item.title,
            release_date=str(search_results_item.releaseDate),
            release_year=search_results_item.releaseDate.year,
            ext=self._caption_file.ext,
            lan=self._caption_file.lan,
            lanName=self._caption_file.lanName,
            delay=self._caption_file.delay,
            size_string=get_filesize_string(self._caption_file.size),
            season=season,
            episode=episode,
        )
        filename_template = (
            self.series_filename_template
            if search_results_item.subjectType == SubjectType.TV_SERIES
            else self.movie_filename_template
        )
        return sanitize_filename(filename_template % placeholders)

    async def run(
        self,
        filename: str | SearchResultsItem,
        dir: str = getcwd(),
        chunk_size: int = 16,
        test: bool = False,
        **kwargs,
    ) -> Path | httpx.Response:
        """Performs the actual download, incase already downloaded then return its Path.

        Args:
            filename (str|SearchResultsItem): Movie filename
            dir (str, optional): Directory for saving the contents Defaults to current directory. Defaults to cwd.
            chunk_size (int, optional): Chunk_size for downloading files in KB. Defaults to 16.
            test (bool, optional): Just test if download is possible but do not actually download. Defaults to False.
            **kwargs: Keyworded arguments for generating filename incase instance of filename is SearchResultsItem.

        Returns:
            Path|httpx.Response: Path where the caption file has been saved to or httpx Response (test).
        """
        if isinstance(filename, SearchResultsItem):
            # Lets generate filename
            filename = self.generate_filename(filename, **kwargs)
        save_to = Path(dir) / filename
        if save_to.exists() and path.getsize(save_to) == self._caption_file.size:
            logger.info(f"Caption file already downloaded - {save_to}.")
            return save_to
        size_with_unit = get_filesize_string(self._caption_file.size)
        logger.info(
            f"Downloading caption file ({size_with_unit}). " f"Writing to ({save_to})"
        )
        async with self.session.stream("GET", str(self._caption_file.url)) as response:
            response.raise_for_status()
            if test:
                logger.info(f"Download test passed successfully {response.__repr__}")
                return response
            with open(save_to, mode="wb") as fh:
                async for chunk in response.aiter_bytes(chunk_size * 1_000):
                    fh.write(chunk)
        logger.info(f"{filename} - {size_with_unit} ✅")
        return save_to
