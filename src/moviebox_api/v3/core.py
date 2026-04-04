from moviebox_api.v3._bases import BaseContentProviderAndHelper
from moviebox_api.v3.helpers import assert_instance
from moviebox_api.v3.http_client import MovieBoxHttpClient


class Homepage(BaseContentProviderAndHelper):
    """Fetches landing page contents"""

    _path = "/wefeed-mobile-bff/tab-operating"

    def __init__(self, client_session: MovieBoxHttpClient):
        """Constructor for `Homepage`"""
        assert_instance(
            client_session, MovieBoxHttpClient, "client_session"
        )
        self.client_session = client_session
        self._page_number: int = 1
        self._tab_id: int = 0
        self._version: str = ""

    def _create_payload(self) -> dict:
        return {
            "page": self._page_number,
            "tabId": self._tab_id,
            "version": self._version
        }

    async def get_content(self) -> dict:
        payload = self._create_payload()
        contents = await self.client_session.get_from_api(
            self._path,
            params=payload
        )
        return contents

    async def get_content_model(self, *args, **kwargs):
        return await super().get_content_model(*args, **kwargs)