"""This module store constant variables"""

import os
import typing as t
from moviebox_api import logger
from enum import IntEnum

mirror_hosts = (
    "moviebox.ng",
    "h5.aoneroom.com",
    "movieboxapp.in",
    "moviebox.pk",
    "moviebox.ph",
    "moviebox.id",
)
"""Mirror domains/subdomains of Moviebox"""

ENVIRONMENT_HOST_KEY = "MOVIEBOX_API_HOST"
"""User declares host to use as environment variable using this key"""

selected_host = (
    os.getenv(ENVIRONMENT_HOST_KEY) or mirror_hosts[0]
)  # TODO: Choose the right value based on working status
"""Host adress only with protocol"""

host_protocol = "https"
"""Host protocol i.e http/https"""

host_url = f"{host_protocol}://{selected_host}/"
"""Complete host adress with protocol"""

logger.info(f"Moviebox host url - {host_url}")

default_request_headers = {
    "X-Client-Info": '{"timezone":"Africa/Nairobi"}',  # TODO: Set this value dynamically.
    "Accept-Language": "en-US,en;q=0.5",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0",
    "Referer": host_url,  # "https://moviebox.ng/movies/titanic-kGoZgiDdff?id=206379412718240440&scene&page_from=search_detail&type=%2Fmovie%2Fdetail",
    "Host": selected_host,
    # "X-Source": "",
}
"""For general http requests other than download"""

download_request_headers = {
    "Accept": "*/*",  # "video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0",
    "Origin": selected_host,
    "Referer": host_url,
}
"""For media and subtitle files download requests"""


downloadQualitiesType: t.TypeAlias = t.Literal[
    "WORST", "BEST", "360P", "480P", "720P", "1080P"
]  # TODO: Add more qualities

DOWNLOAD_QUALITIES = (
    "WORST",
    "BEST",
    "360P",
    "480P",
    "720P",
    "1080P",
)  # TODO: Add more qualities


DEFAULT_CAPTION_LANGUAGE = "English"

DEFAULT_SHORT_CAPTION_LANGUAGE = "en"


class SubjectType(IntEnum):
    """Content types mapped to their integer representatives"""

    ALL = 0
    """Both Movies, series and music contents"""
    MOVIES = 1
    """Movies content only"""
    TV_SERIES = 2
    """TV Series content only"""
    MUSIC = 6
    """Music contents only"""

    @classmethod
    def map(cls) -> dict[str, int]:
        """Content-type names mapped to their int representatives"""
        resp = {}
        for entry in cls:
            resp[entry.name] = entry.value
        return resp
