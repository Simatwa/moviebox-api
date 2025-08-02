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
    async def get_content(self) -> Dict | str:
        """Response as received from server"""
        raise NotImplementedError("Function needs to be implemented in subclass.")

    @abstractmethod
    async def get_modelled_content(self) -> object:
        """Modelled version of the content"""
        raise NotImplementedError("Function needs to be implemented in subclass.")


class ContentProviderHelper:
    """Provides common methods to content proder classes"""


class BaseContentProviderAndHelper(BaseContentProvider, ContentProviderHelper):
    """A class that inherits both `BaseContentProvider(ABC)` and `ContentProviderHelper`"""
