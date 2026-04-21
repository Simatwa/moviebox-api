import asyncio
import os
from abc import ABC, abstractmethod
from pathlib import Path

import httpx
from throttlebuster import DownloadedFile, ThrottleBuster

from moviebox_api.v1._bases import (
    BaseContentProviderAndHelper,
)
from moviebox_api.v3.constants import (
    CURRENT_WORKING_DIR,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_TASKS,
    DOWNLOAD_PART_EXTENSION,
    DOWNLOAD_REQUEST_HEADERS,
)

# from moviebox_api.v3.models.downloadables import (
# RootDownloadableFilesDetailModel 
# )


class BaseFileDownloader(ABC):
    """Base class for media and caption files downloader"""

    @abstractmethod
    async def run(self, *args, **kwargs) -> DownloadedFile | httpx.Response:
        """Downloads a movie or caption file"""
        raise NotImplementedError("Function needs to be implemented in subclass.")


class FileDownloaderHelper:
    """Provide common method to file downloaders"""

    def run_sync(self, *args, **kwargs) -> DownloadedFile | httpx.Response:
        """Sychronously performs the actual download"""
        return asyncio.get_event_loop().run_until_complete(
            self.run(*args, **kwargs)
        )


class BaseFileDownloaderAndHelper(FileDownloaderHelper, BaseFileDownloader):
    """Inherits both `FileDownloaderHelper` and `BaseFileDownloader`"""

    request_headers = DOWNLOAD_REQUEST_HEADERS
    request_cookies = {}

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
        """Constructor for `BaseFileDownloaderAndHelper`

        Args:
            dir (Path | str, optional): Directory for saving downloaded files to. 
                Defaults to CURRENT_WORKING_DIR.
            chunk_size (int, optional): Streaming download chunk size in kilobytes
                . Defaults to DEFAULT_CHUNK_SIZE.
            tasks (int, optional): Number of tasks to carry out the download. 
                Defaults to DEFAULT_TASKS.
            part_dir (Path | str, optional): Directory for temporarily saving 
                downloaded file-parts to. Defaults to CURRENT_WORKING_DIR.
            part_extension (str, optional): Filename extension for download parts
                . Defaults to DOWNLOAD_PART_EXTENSION.
            merge_buffer_size (int|None, optional). Buffer size for merging the
                 separated files in kilobytes. Defaults to chunk_size.
            group_series(bool, optional): Create directory for a series & group 
                episodes based on season number. Defaults to False.

        httpx_kwargs : Keyword arguments for `httpx.AsyncClient`
        """

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

    @classmethod
    def create_final_dir(
        cls,
        working_dir: Path,
        downloadable_files_detail: object,  # RootDownloadableFilesDetailModel,
        season: int,
        episode: int,
        test: bool,
        group: bool,
    ):
        if group and season and episode:
            # series it is
            working_dir = Path(working_dir)
            assert working_dir.exists(), (
                f"The chosen working directory does not exist - {working_dir}"
            )

            final_dir = working_dir.joinpath(
                f"{downloadable_files_detail.subject_title} "
                f"({downloadable_files_detail.release_date.year})",
                f"S{season}",
            )

            if not test:
                os.makedirs(final_dir, exist_ok=True)

            return final_dir

        return working_dir
