import asyncio
import os
from abc import ABC, abstractmethod
from pathlib import Path

import httpx
from throttlebuster import DownloadedFile

from moviebox_api.v1._bases import (
    BaseContentProviderAndHelper,
)

# from moviebox_api.v3.models.downloadables import RootDownloadableFilesDetailModel


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
