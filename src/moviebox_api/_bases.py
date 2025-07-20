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
    async def get_modelled_content(self):
        """Modelled version of the content"""
        raise NotImplementedError("Function needs to be implemented in subclass.")


class ContentProviderHelper:
    """Provides common methods to content proder classes"""

    async def _update_content(self, dry: bool = False) -> Dict:
        """Fetch contents and update it.

        Args:
            dry (bool): Do not update if previously fetched. Defaults to False.

        Returns:
            Dict: Home contents
        """
        if self.__content is not None and dry == True:
            # Dry update
            pass
        else:
            self.__content = await self.session.get_from_api(self._url)

        return self.__content


class BaseContentProviderAndHelper(BaseContentProvider, ContentProviderHelper):
    """A class that inherits both `BaseContentProvider(ABC)` and `ContentProviderHelper`"""
