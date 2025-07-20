"""
Provide ways to interact with moviebox using `httpx`
"""

import httpx
from httpx import Response
from httpx._config import DEFAULT_TIMEOUT_CONFIG
from typing import Dict
from moviebox_api.models import MovieboxAppInfo
from moviebox_api.utils import process_api_response

default_request_headers = {
    "X-Client-Info": '{"timezone":"Africa/Nairobi"}',
    "Accept-Language": "en-US,en;q=0.5",
    "Accept": "*/*,",  # "application/json",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0",
    # "Referer":	"https://moviebox.ng/movies/the-basketball-diaries-GpkJMWty103?id=2518237873669820192&scene&page_from=search_detail&type=%2Fmovie%2Fdetail",
    "Host": "moviebox.ng",
    # "Alt-Used" :	"moviebox.n"
}

# TODO : Set timezone and language values based on user's machine

request_cookies = {}

__all__ = ["Session", "default_request_headers"]


class Session:
    """Performs actual get http requests asynchronously
    with or without cookies on demand
    """

    _moviebox_app_info_url = (
        r"https://moviebox.ng/wefeed-h5-bff/app/get-latest-app-pkgs?app_name=moviebox"
    )

    def __init__(
        self,
        headers: Dict = default_request_headers,
        cookies: Dict = request_cookies,
        timeout: float | int = DEFAULT_TIMEOUT_CONFIG,
    ):
        """Constructor for `Session`

        Args:
            headers (Dict, optional): Http request headers. Defaults to request_headers.
            cookies (Dict, optional): Http request cookies. Defaults to request_cookies.
            timeout (int|float, optional): Http request timeout in seconds. Defaults to DEFAULT_TIMEOUT_CONFIG.
        """
        self._headers = headers
        self._cookies = cookies
        self._timeout = timeout
        self._client = httpx.AsyncClient(
            headers=headers, cookies=cookies, timeout=timeout
        )
        self.moviebox_app_info: MovieboxAppInfo | None = None
        self.__moviebox_app_info_fetched: bool = False
        """Used to track cookies assignment status"""

    def __repr__(self):
        return rf"<Session(MovieBoxAPI) timeout={self._timeout}>"

    async def get(self, url: str, params: Dict = {}, **kwargs) -> Response:
        """Makes a http get request without server cookies from previous requests.
        It's relevant because some requests with expired cookies won't go through
        but having it none does go through.

        Args:
            url (str): Resource link.
            params (Dict, optional): Request params. Defaults to {}.

        Returns:
            Response: Httpx response object
        """
        client = httpx.AsyncClient(
            headers=self._headers, cookies=self._cookies, **kwargs
        )
        response = await client.get(url, params=params)
        return response.raise_for_status()

    async def get_from_api(self, *args, **kwargs) -> Dict:
        """Fetch data from api and extract the `data` field from the response

        Returns:
            Dict: Extracted data field value
        """
        response = await self.get(*args, **kwargs)
        return process_api_response(response.json())

    async def get_with_cookies(self, url: str, params: Dict = {}, **kwargs) -> Response:
        """Makes a http get request without server-assigned cookies from previous requests.

        Args:
            url (str): Resource link.
            params (Dict, optional): Request params. Defaults to {}.

        Returns:
            Response: Httpx response object
        """
        await self.ensure_cookies_are_assigned()
        response = await self._client.get(url, params=params, **kwargs)
        return response.raise_for_status()

    async def get_with_cookies_from_api(self, *args, **kwargs) -> Dict:
        """Makes a http get request without server-assigned cookies from previous requests
        and extract the `data` field from the response.

        Returns:
            Dict: Extracted data field value
        """
        response = await self.get_with_cookies(*args, **kwargs)
        return process_api_response(response.json())

    async def post(self, url: str, json: dict, **kwargs) -> Response:
        """Makes a http post request with both self assigned and server-
        assigned cookies

        Args:
            url (str): Resource link
            json (dict): Data to be send.

        Returns:
            Response: Httpx response object
        """
        await self.ensure_cookies_are_assigned()
        response = await self._client.post(url, json=json, **kwargs)
        return response.raise_for_status()

    async def post_to_api(self, *args, **kwargs) -> Dict:
        """Sends data to api and extract the `data` field from the response

        Returns:
            Dict: Extracted data field value
        """
        response = await self.post(*args, **kwargs)
        return process_api_response(response.json())

    async def ensure_cookies_are_assigned(self) -> bool:
        """Checks if the essential cookies are available
        if not it update.

        Returns:
            bool: `account` cookie availability status.
        """
        if not self.__moviebox_app_info_fetched:
            # First run probably
            await self._fetch_app_info()
            self.__moviebox_app_info_fetched = True
        return self._client.cookies.get("acoount") is not None

    async def _fetch_app_info(self) -> MovieboxAppInfo:
        """Fetches the moviebox app info but the main goal
        is to get the essential cookies required for requests
        such as download to go through.

        Returns:
            MovieboxAppInfo: Details about latest moviebox app
        """
        response = await self._client.get(url=self._moviebox_app_info_url)
        response.raise_for_status()
        moviebox_app_info = process_api_response(response.json())
        if isinstance(moviebox_app_info, list):
            moviebox_app_info = moviebox_app_info[0]
        self.moviebox_app_info = MovieboxAppInfo(**moviebox_app_info)
        return self.moviebox_app_info

    update_session_cookies = _fetch_app_info
