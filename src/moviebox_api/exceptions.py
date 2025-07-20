"""Exceptions module"""

from typing import Dict
from moviebox_api._bases import BaseMovieboxException


class MovieboxApiException(BaseMovieboxException):
    """A unique `Exception` for the package"""


class UnsuccessfulResponseError(BaseMovieboxException):
    """Raised when moviebox API serves request with a fail report."""

    def __init__(self, response: Dict, *args, **kwargs):
        self.response = response
        """Unsuccessful response data"""
        super().__self__(*args, **kwargs)


class ExhaustedSearchResultsError(BaseMovieboxException):
    """Raised when trying to navigate to next page of a complete search results"""

    def __init__(self, last_pager, *args, **kwargs):
        self.last_pager = self.last_pager
        """Page info of the current page"""
        super().__init__(*args, **kwargs)
