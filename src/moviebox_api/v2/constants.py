"""This module stores constant variables"""

import os

from moviebox_api.v1.constants import SubjectType
from moviebox_api.v2 import logger

"""asyncio event loop"""

MIRROR_HOSTS = ("h5-api.aoneroom.com",)
"""Mirror domains/subdomains of Moviebox-api"""

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

logger.info(f"Moviebox API host url - {HOST_URL}")

REFERER = "https://videodownloader.site/"

DEFAULT_REQUEST_HEADERS = {
    "X-Client-Info": '{"timezone":"Africa/Nairobi"}',
    # TODO: Set this value dynamically.
    "Accept-Language": "en-US,en;q=0.5",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101"
    " Firefox/137.0",
    "Referer": REFERER,
}
"""For general http requests other than download"""

DOWNLOAD_REQUEST_REFERER = REFERER

DOWNLOAD_REQUEST_HEADERS = {
    "Accept": "*/*",  # "video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,
    # audio/*;q=0.6,*/*;q=0.5",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 "
    "Firefox/137.0",
    "Origin": REFERER,
    "Referer": DOWNLOAD_REQUEST_REFERER,
}
"""For media and subtitle files download requests"""

SINGLE_ITEM_SUBJECT_TYPES = {
    SubjectType.MUSIC,
    SubjectType.MOVIES,
    SubjectType.ANIME,
    SubjectType.EDUCATION,
}
