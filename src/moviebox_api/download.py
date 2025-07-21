from typing import Dict
from moviebox_api._bases import BaseContentProvider
from moviebox_api.models import (
    SearchResultsItem,
    DownloadableFilesMetadata,
    MediaFileMetadata,
    CaptionFileMetadata,
)
from moviebox_api.requests import Session
from moviebox_api.utils import (
    assert_instance,
    get_absolute_url,
    host_url,
    get_filesize_string,
)
from os import getcwd, path
from pathlib import Path
from tqdm import tqdm
import httpx
from moviebox_api import logger


class DownloadableFilesDetail(BaseContentProvider):
    _url = get_absolute_url(r"/wefeed-h5-bff/web/subject/download")

    def __init__(self, session: Session, item: SearchResultsItem):
        """Constructor for `DownloadbleFilesDetail`

        Args:
            session (Session): MovieboxAPI request session.
            item (SearchResultsItem): Movie item to handle.
        """
        assert_instance(session, Session, "session")
        assert_instance(item, SearchResultsItem, "item")
        self.session = session
        self._item = item

    def _create_request_params(self) -> Dict:
        """Creates request parameters
        Returns:
            Dict: Request params
        """
        # se -> season
        # ep -> episode
        return {"subjectId": self._item.subjectId, "se": 0, "ep": 0}

    async def get_content(self) -> Dict:
        """Performs the actual fetching of files detail.

        Returns:
            Dict: File details
        """
        # Refererer
        request_header = {
            "Referer": get_absolute_url(f"/movies/{self._item.detailPath}")
        }
        # Without the referer, empty response will be served.

        content = await self.session.get_with_cookies_from_api(
            url=self._url,
            params=self._create_request_params(),
            headers=request_header,
        )
        return content

    async def get_modelled_content(self) -> DownloadableFilesMetadata:
        """Get modelled version of the downloadable files detail.

        Returns:
            DownloadableFilesMetadata: Modelled file details
        """
        contents = await self.get_content()
        return DownloadableFilesMetadata(**contents)


class MediaFileDownloader:
    """Makes a remote media file available locally"""

    request_headers = {
        "Accept": "video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0",
        "Origin": "moviebox.ng",
    }
    request_cookies = {}

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

    async def run(
        self,
        filename: str,
        dir: str = getcwd(),
        progress_bar=True,
        quiet: bool = False,
        chunk_size: int = 512,
        resume: bool = False,
        leave: bool = True,
        colour: str = "cyan",
        simple: bool = True,
    ):
        """Performs the actual download.
        Args:
            filename (str): Movie filename
            dir (str, optional): Directory for saving the contents Defaults to current directory.
            progress_bar (bool, optional): Display download progress bar. Defaults to True.
            quiet (bool, optional): Not to stdout anything. Defaults to False.
            chunk_size (int, optional): Chunk_size for downloading files in KB. Defaults to 512.
            resume (bool, optional):  Resume the incomplete download. Defaults to False.
            leave (bool, optional): Keep all leaves of the progressbar. Defaults to True.
            colour (str, optional): Progress bar display color. Defaults to "cyan".
            simple (bool, optional): Show percentage and bar only in progressbar. Deafults to False.

        Raises:
            FileExistsError:  Incase of `resume=True` but the download was complete

        Returns:
            str: Path where the media file has been saved to.
        """
        current_downloaded_size = 0
        current_downloaded_size_in_mb = 0
        save_to = Path(dir) / filename

        def pop_range_in_session_headers():
            if self.session.headers.get("Range"):
                self.session.headers.pop("Range")

        if resume:
            assert path.exists(save_to), f"File not found in path - '{save_to}'"
            current_downloaded_size = path.getsize(save_to)
            # Set the headers to resume download from the last byte
            self.session.headers.update({"Range": f"bytes={current_downloaded_size}-"})
            current_downloaded_size_in_mb = current_downloaded_size / 1000000

        size_in_bytes = self._media_file.size

        if resume:
            assert (
                size_in_bytes != current_downloaded_size
            ), f"Download completed for the file in path - '{save_to}'"

        size_in_mb = (size_in_bytes / 1_000_000) + current_downloaded_size_in_mb
        size_with_unit = get_filesize_string(self._media_file.size)
        chunk_size_in_bytes = chunk_size * 1_000

        saving_mode = "ab" if resume else "wb"
        if progress_bar:
            if not quiet:
                print(f"{filename}")
            async with self.session.stream(
                "GET", str(self._media_file.url)
            ) as response:
                response.raise_for_status()
                with open(save_to, saving_mode) as fh:
                    p_bar = tqdm(
                        total=round(size_in_mb, 1),
                        unit="Mb",
                        unit_scale=True,
                        colour=colour,
                        leave=leave,
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
            return save_to
        else:
            logger.debug(f"Movie file info {self._media_file}")
            logger.info(
                f"[{size_with_unit}] Downloading media. (Resume : {resume}) "
                f"writing to ({save_to})"
            )
            async with self.session.stream(
                "GET", str(self._media_file.url)
            ) as response:
                response.raise_for_status()
                with open(save_to, saving_mode) as fh:
                    async for chunk in response.aiter_bytes(chunk_size_in_bytes):
                        fh.write(chunk)
            pop_range_in_session_headers()
            logger.info(f"{filename} - {size_with_unit} ✅")
            pop_range_in_session_headers()
            return save_to


class CaptionFileDownloader:
    """Makes a local copy of a remote subtitle/caption file"""

    request_headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0",
        "Origin": host_url,
    }
    request_cookies = {}

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

    async def run(
        self,
        filename: str,
        dir: str = getcwd(),
        chunk_size: int = 16,
    ):
        """Performs the actual download.
        Args:
            filename (str): Movie filename
            dir (str, optional): Directory for saving the contents Defaults to current directory. Defaults to cwd.
            chunk_size (int, optional): Chunk_size for downloading files in KB. Defaults to 16.

        Returns:
            str: Path where the caption file has been saved to.
        """
        save_to = Path(dir) / filename
        async with self.session.stream("GET", str(self._caption_file.url)) as response:
            response.raise_for_status()
            with open(save_to, mode="wb") as fh:
                async for chunk in response.aiter_bytes(chunk_size * 1_000):
                    fh.write(chunk)
        return save_to
