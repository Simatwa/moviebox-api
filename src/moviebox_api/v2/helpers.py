"""V2 Helpers"""

import re

import moviebox_api.v1.helpers
from moviebox_api.v2.constants import HOST_URL

VALID_DETAIL_PATH_PATTERN = re.compile(r"^[\w-]+-\w{9,13}$")

VALID_GENRE_TOP_ID_PATTERN = re.compile(r"^\d{17,19}$")


def get_absolute_url(relative_url: str, base_url: str = HOST_URL):

    return moviebox_api.v1.helpers.get_absolute_url(relative_url, base_url)


def validate_detail_path(path: str) -> bool:
    return VALID_DETAIL_PATH_PATTERN.match(path) is not None


def validate_genre_top_id(value: str) -> bool:
    return VALID_GENRE_TOP_ID_PATTERN.match(value) is not None
