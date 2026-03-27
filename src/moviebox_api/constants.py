"""This module stores constant variables"""

import os
import typing as t
from enum import IntEnum, StrEnum
from pathlib import Path

from throttlebuster.constants import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_READ_TIMEOUT_ATTEMPTS,
    DEFAULT_TASKS_LIMIT,
    DOWNLOAD_PART_EXTENSION,
    DownloadMode,
)

from moviebox_api import logger

"""asyncio event loop"""

MIRROR_HOSTS = (
    # "moviebox.ng",
    "h5.aoneroom.com",
    "movieboxapp.in",
    "moviebox.pk",
    "moviebox.ph",
    "moviebox.id",
    # "fmoviesunblocked.net"
    "v.moviebox.ph",
    "netnaija.video",
    # "sflix.film",
    # "netnaija.com"
)
"""Mirror domains/subdomains of Moviebox"""

ENVIRONMENT_HOST_KEY = "MOVIEBOX_API_HOST"
"""User declares host to use as environment variable using this key"""

SELECTED_HOST = (
    os.getenv(ENVIRONMENT_HOST_KEY) or MIRROR_HOSTS[0]
)  # TODO: Choose the right value based on working status
"""Host adress only with protocol"""

HOST_PROTOCOL = "https"
"""Host protocol i.e http/https"""

HOST_URL = f"{HOST_PROTOCOL}://{SELECTED_HOST}/"
"""Complete host adress with protocol"""

logger.info(f"Moviebox host url - {HOST_URL}")

DEFAULT_REQUEST_HEADERS = {
    "X-Client-Info": '{"timezone":"Africa/Nairobi"}',  # TODO: Set this value dynamically.
    "Accept-Language": "en-US,en;q=0.5",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0",
    "Referer": HOST_URL,  # "https://moviebox.ng/movies/titanic-kGoZgiDdff?id=206379412718240440&scene&page_from=search_detail&type=%2Fmovie%2Fdetail",
    "Host": SELECTED_HOST,
    # "X-Source": "",
}
"""For general http requests other than download"""

DOWNLOAD_REQUEST_REFERER = "https://fmoviesunblocked.net/"

DOWNLOAD_REQUEST_HEADERS = {
    "Accept": "*/*",  # "video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0",
    "Origin": SELECTED_HOST,
    "Referer": DOWNLOAD_REQUEST_REFERER,
}
"""For media and subtitle files download requests"""


DownloadQualitiesType: t.TypeAlias = t.Literal[
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

DEFAULT_CAPTION_LANGUAGE_SHORT = "en"

CURRENT_WORKING_DIR = Path(os.getcwd())
"""Directory where contents will be saved to by default"""

ITEM_DETAILS_PATH = "/detail"
"""Immediate path to particular item details page"""


DEFAULT_TASKS = 5
"""Default number of connections for download"""


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

    UNKNOWN_1 = 5
    """Yet to be known"""

    UNKNOWN = 7
    """Yet to be known"""

    # TODO: Research and update UNKNOWNS

    @classmethod
    def map(cls) -> dict[str, int]:
        """Content-type names mapped to their int representatives"""
        resp = {}
        for entry in cls:
            resp[entry.name] = entry.value
        return resp


class DownloadStatus(StrEnum):
    DOWNLOADING = "downloading"
    FINISHED = "finished"
