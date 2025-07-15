""" 
Main module for the package
"""

from moviebox_api.requests import Session
from moviebox_api.utils import assert_instance
from moviebox_api._bases import BaseContentProvider
from moviebox_api.models import HomepageContentModel
from typing import Dict


class Homepage(BaseContentProvider):
    """Content listings on landing page"""

    _url = r"https://moviebox.ng/wefeed-h5-bff/web/home"

    def __init__(self, session: Session):
        """Constructtor `Home`

        Args:
            session (Session): MovieboxAPI request session
        """
        assert_instance(session, Session, "session")
        self.session = session
        self.__content: Dict | None = None

    async def get_content(self) -> Dict:
        """Landing page contents

        Returns:
            Dict
        """
        if self.__content is None:
            await self._update_content()
        return self.__content

    async def _update_content(self, dry: bool = False) -> Dict:
        """Fetch home page contents and update it.

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

    async def get_modelled_content(self) -> HomepageContentModel:
        """Modelled version of the contents"""
        await self._update_content(dry=True)
        return HomepageContentModel(**self.__content)


class EveryoneSearches:
    """Movies and series everyone searches"""

    _url = r"https://moviebox.ng/wefeed-h5-bff/web/subject/everyone-search"

    def __init__(self, session: Session):
        """Constructor for `EveryoneSearches`

        Args:
            session (Session): MovieboxAPI request session
        """
        assert_instance(session, Session, "session")
