"""Exceptions module"""

from pathlib import Path

from httpx import Response

from moviebox_api._bases import BaseMovieboxException


class MovieboxApiException(BaseMovieboxException):
    """A unique `Exception` for the package"""


class UnsuccessfulResponseError(BaseMovieboxException):
    """Raised when moviebox API serves request with a fail report."""

    def __init__(self, response: dict, *args, **kwargs):
        self.response = response
        """Unsuccessful response data"""
        super().__init__(*args, **kwargs)


class EmptyResponseError(BaseMovieboxException):
    """Raised when an empty body response is received with status code 200-OK"""

    def __init__(self, response: Response, *args, **kwargs):
        self.response = response
        """Httpx response object"""
        super().__init__(*args, **kwargs)


class ExhaustedSearchResultsError(BaseMovieboxException):
    """Raised when trying to navigate to next page of a complete search results"""

    def __init__(self, last_pager, *args, **kwargs):
        self.last_pager = last_pager
        """Current page info"""
        super().__init__(*args, **kwargs)


class ZeroSearchResultsError(BaseMovieboxException):
    """Raised when empty search results is encountered."""


class DownloadCompletedError(BaseMovieboxException):
    """Raised whren attempting to resume a complete download."""

    def __init__(self, saved_to: Path, *args, **kwargs):
        self.saved_to = saved_to
        """Path to the already downloaded movie/tv-series file"""
        super().__init__(*args, **kwargs)


class ZeroCaptionFileError(BaseMovieboxException):
    """Raised when caption file is required but the item lacks any"""


class ZeroMediaFileError(BaseMovieboxException):
    """Raised when trying to access a downloadable media file but the list is empty"""
