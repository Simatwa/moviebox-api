"""
Async HTTP transport layer.

Wraps ``httpx.AsyncClient`` and provides host-pool fallback so that if a
host responds with a retryable status code the next host in the pool is tried
automatically.
"""

from __future__ import annotations

import json
import logging
from json import dumps
from typing import Any

import httpx

from moviebox_api.v3.constants import (
    AUTH_TOKEN,
    CLIENT_INFO,
    RETRY_STATUS_CODES,
    USER_AGENT,
)
from moviebox_api.v3.crypto import build_signed_headers
from moviebox_api.v3.helpers import (
    combine_url_path_with_params,
    process_api_response,
)
from moviebox_api.v3.urls import DEFAULT_API_BASE, HOST_POOL

logger = logging.getLogger(__name__)


class MovieBoxHttpClient:
    """
    Async HTTP client for the MovieBox API with:

    * Automatic host-pool fallback on retryable error codes.
    * Request signing (``X-Client-Token``, ``x-tr-signature``).
    * Transparent bearer-token refresh from ``x-user`` response headers.
    """

    def __init__(
        self,
        host_pool: list[str] = HOST_POOL,
        timeout: float = 20.0,
        follow_redirects: bool = True,
        **httpx_client_kwargs,
    ) -> None:
        self._host_pool = host_pool
        self._active_base: str = DEFAULT_API_BASE
        self._runtime_token: str | None = None
        self._client: httpx.AsyncClient | None = None
        self._timeout = timeout
        self._follow_redirects = follow_redirects
        self._httpx_client_kwargs = httpx_client_kwargs

    async def __aenter__(self) -> MovieBoxHttpClient:
        self._client = httpx.AsyncClient(
            timeout=self._timeout,
            follow_redirects=self._follow_redirects,
            **self._httpx_client_kwargs,
        )
        return self

    async def __aexit__(self, *_: Any) -> None:
        if self._client:
            await self._client.aclose()

    @property
    def active_base(self) -> str:
        return self._active_base

    @property
    def _effective_token(self) -> str | None:
        return self._runtime_token or AUTH_TOKEN

    def _absorb_x_user(self, headers: httpx.Headers) -> None:
        x_user = headers.get("x-user", "")
        if not x_user:
            return
        try:
            payload = json.loads(x_user)
            token = payload.get("token", "")
            if token:
                self._runtime_token = token
        except (json.JSONDecodeError, AttributeError):
            pass

    def _signed_headers(
        self,
        method: str,
        url: str,
        accept: str = "application/json",
        content_type: str = "application/json",
        body: str | None = None,
        include_play_mode: bool = False,
    ) -> dict[str, str]:
        return build_signed_headers(
            method=method,
            url=url,
            accept=accept,
            content_type=content_type,
            body=body,
            include_play_mode=include_play_mode,
            auth_token=self._effective_token,
            client_info=CLIENT_INFO,
            user_agent=USER_AGENT,
        )

    async def _request(
        self,
        method: str,
        path_and_query: str,
        *,
        accept: str = "application/json",
        content_type: str = "application/json",
        body: str | None = None,
        include_play_mode: bool = False,
        **request_kwargs,
    ) -> tuple[str, httpx.Response]:
        """
        Try each host in the pool in order and return the first response that
        is NOT a retryable status code.

        Returns ``(winning_base_url, response)``.
        """
        assert self._client is not None, (
            "Client not started – use 'async with' context."
        )

        last_response: httpx.Response | None = None
        last_base: str = self._active_base

        for base in self._host_pool:
            url = f"{base}{path_and_query}"
            headers = self._signed_headers(
                method, url, accept, content_type, body, include_play_mode
            )

            try:
                if method.upper() == "GET":
                    response = await self._client.get(
                        url, headers=headers, **request_kwargs
                    )
                else:
                    response = await self._client.post(
                        url,
                        headers=headers,
                        content=body.encode() if body else b"",
                        **request_kwargs,
                    )

                self._absorb_x_user(response.headers)
                last_response = response
                last_base = base

                if response.status_code not in RETRY_STATUS_CODES:
                    self._active_base = base
                    return base, response

                logger.debug(
                    "Host %s returned %d – retrying.", base, response.status_code
                )

            except httpx.TransportError as exc:
                logger.debug("Host %s transport error: %s", base, exc)

        # All hosts failed; return whatever we got last
        self._active_base = last_base
        if last_response is None:
            raise RuntimeError(f"All hosts exhausted for {path_and_query}")
        return last_base, last_response

    async def get(
        self,
        path: str,
        *,
        params: dict = None,
        accept: str = "application/json",
        content_type: str = "application/json",
        include_play_mode: bool = False,
    ) -> tuple[str, httpx.Response]:
        if params:
            path = combine_url_path_with_params(path, params)

        return await self._request(
            "GET",
            path,
            accept=accept,
            content_type=content_type,
            include_play_mode=include_play_mode,
        )

    async def post(
        self,
        path: str,
        json: dict,
        *,
        params: dict = None,
        accept: str = "application/json",
        content_type: str = "application/json; charset=utf-8",
        **request_kwargs,
    ) -> tuple[str, httpx.Response]:

        if params:
            path = combine_url_path_with_params(path, params)

        return await self._request(
            "POST",
            path,
            accept=accept,
            content_type=content_type,
            body=dumps(json),
            **request_kwargs,
        )

    async def get_raw(
        self,
        full_url: str,
        *,
        params: dict = None,
        headers: dict[str, str] | None = None,
        **request_kwargs,
    ) -> httpx.Response:
        """
        Fetch an arbitrary URL without signing (used for web-API scraping and
        extractor fallbacks).
        """
        if params:
            full_url = combine_url_path_with_params(full_url, params)

        assert self._client is not None
        return await self._client.get(
            full_url, headers=headers or {}, **request_kwargs
        )

    async def get_from_api(self, *args, **kwargs) -> dict:
        """Fetch data from api and extract the `data` field from the response

        Returns:
            dict: Extracted data field value
        """
        _, response = await self.get(*args, **kwargs)
        return process_api_response(response.json())

    async def post_to_api(self, *args, **kwargs) -> dict:
        """Sends data to api and extract the `data` field from the response

        Returns:
            dict: Extracted data field value
        """
        _, response = await self.post(*args, **kwargs)
        return process_api_response(response.json())
