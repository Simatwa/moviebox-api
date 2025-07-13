""" 
This module contains base classes for the entire package
"""
from typing import Dict
from moviebox_api.requests import Session

class BaseMovieboxException(Exception):
    """All exception classes of this package inherits this class"""

class BaseContentProvider:
    """Provides easy retrieval of resource from moviebox"""

    @property
    def content(self) -> Dict|str:
        """Contents of homepage
        """
        return self.__content