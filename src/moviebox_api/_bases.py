"""
This module contains base classes for the entire package
"""

import asyncio
import os
from abc import ABC, abstractmethod
from pathlib import Path

import httpx
from throttlebuster import DownloadedFile

# from moviebox_api.models import SearchResultsItem


class BaseMovieboxException(Exception):
    """Base class for all exceptions of this package"""


class BaseContentProvider(ABC):
    """Provides easy retrieval of resource from moviebox"""

    @abstractmethod
    async def get_content(self, *args, **kwargs) -> dict | list[dict]:
        """Response as received from server"""
        raise NotImplementedError("Function needs to be implemented in subclass.")

    @abstractmethod
    async def get_content_model(self, *args, **kwargs) -> object | list[object]:
        """Modelled version of the content"""
        raise NotImplementedError("Function needs to be implemented in subclass.")


class ContentProviderHelper:
    """Provides common methods to content provider classes"""

    def get_content_sync(self, *args, **kwargs) -> dict | list[dict]:
        """Get content `synchronously`"""
        return asyncio.get_event_loop().run_until_complete(self.get_content(*args, **kwargs))

    def get_content_model_sync(self, *args, **kwargs) -> object | list[object]:
        """Get content model `synchronously`"""
        return asyncio.get_event_loop().run_until_complete(self.get_content_model(*args, **kwargs))


class BaseContentProviderAndHelper(BaseContentProvider, ContentProviderHelper):
    """A class that inherits both `BaseContentProvider(ABC)` and `ContentProviderHelper`"""


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
        return asyncio.get_event_loop().run_until_complete(self.run(*args, **kwargs))


class BaseFileDownloaderAndHelper(FileDownloaderHelper, BaseFileDownloader):
    """Inherits both `FileDownloaderHelper` and `BaseFileDownloader`"""

    @classmethod
    def create_final_dir(
        cls,
        working_dir: Path,
        search_results_item: object,  # "SearchResultsItem",
        season: int,
        episode: int,
        test: bool,
        group: bool,
    ):
        if group and season and episode:
            # series it is
            working_dir = Path(working_dir)
            assert working_dir.exists(), f"The chosen working directory does not exist - {working_dir}"

            final_dir = working_dir.joinpath(
                f"{search_results_item.title} ({search_results_item.releaseDate.year})", f"S{season}"
            )

            if not test:
                os.makedirs(final_dir, exist_ok=True)

            return final_dir

        return working_dir
