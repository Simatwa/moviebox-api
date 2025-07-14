""" 
This module contains base classes for the entire package
"""

from typing import Dict
from moviebox_api.requests import Session
from abc import ABC, abstractmethod


class BaseMovieboxException(Exception):
    """All exception classes of this package inherits this class"""


class BaseContentProvider(ABC):
    """Provides easy retrieval of resource from moviebox"""

    @property
    def content(self) -> Dict | str:
        """Contents of homepage"""
        return self.__content

    @property
    @abstractmethod
    def modelled_content(self):
        """Modelled version of the contents"""
        raise NotImplementedError("Function needs to be implemented in subclass.")
