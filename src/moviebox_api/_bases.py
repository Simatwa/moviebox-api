"""
This module contains base classes for the entire package
"""

import asyncio
from abc import ABC, abstractmethod

import httpx
from throttlebuster import DownloadedFile


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
