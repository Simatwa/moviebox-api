""" 
This module contains base classes for the entire package
"""

from typing import Dict
from abc import ABC, abstractmethod


class BaseMovieboxException(Exception):
    """All exception classes of this package inherits this class"""


class BaseContentProvider(ABC):
    """Provides easy retrieval of resource from moviebox"""

    @abstractmethod
    def get_content(self) -> Dict | str:
        """Response as revceived from server"""
        raise NotImplementedError("Function needs to be implemented in subclass.")

    @abstractmethod
    def get_modelled_content(self):
        """Modelled version of the content"""
        raise NotImplementedError("Function needs to be implemented in subclass.")
