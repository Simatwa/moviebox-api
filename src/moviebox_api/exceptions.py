"""Exceptions module"""

from typing import Dict


class BaseMovieboxException(Exception):
    """Base exception  class for the package's exception"""


class UnsuccessfulResponse(BaseMovieboxException):
    """Raised when moviebox API serves request with a fail report."""

    def __init__(self, response: Dict, *args, **kwargs):
        self.response = response
        """Unsuccessful response data"""
        super().__self__(*args, **kwargs)
