"""For server interaction"""

from httpx._config import DEFAULT_TIMEOUT_CONFIG
from httpx._types import (
    CookieTypes,
    ProxyTypes,
    TimeoutTypes,
)

import moviebox_api.v1.requests
from moviebox_api.v2.constants import DOWNLOAD_REQUEST_HEADERS

request_cookies = {}

__all__ = ["Session"]


class Session(moviebox_api.v1.requests.Session):
    _moviebox_app_info_url = None

    def __init__(
        self,
        headers: ProxyTypes | None = DOWNLOAD_REQUEST_HEADERS,
        cookies: CookieTypes | None = request_cookies,
        timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG,
        proxy: ProxyTypes | None = None,
        **httpx_kwargs,
    ):
        """Constructor for `Session`

        Args:
            headers (ProxyTypes | None, optional): Http request headers. Defaults to DOWNLOAD_REQUEST_HEADERS.
            cookies (CookieTypes | None , optional): Http request cookies. Defaults to request_cookies.
            timeout (TimeoutTypes, optional): Http request timeout in seconds. Defaults to DEFAULT_TIMEOUT_CONFIG.
            proxy (ProxyTypes | None, optional): Http requests proxy. Defaults to None.

        httpx_kwargs : Other keyword arguments for `httpx.AsyncClient`
        """  # noqa: E501

        super().__init__(
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            proxy=proxy,
            **httpx_kwargs,
        )

    async def ensure_cookies_are_assigned(self) -> bool:
        return True

    async def _fetch_app_info(self) -> None:
        raise NotImplementedError(
            "This functionality is only available to V1 of moviebox_api.requests"
        )
