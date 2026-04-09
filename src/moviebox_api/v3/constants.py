"""
Constants for moviebox_api.v3
"""

import os
import random
import re
import uuid
from enum import IntEnum, StrEnum

from moviebox_api.v1.constants import (
    CURRENT_WORKING_DIR,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_READ_TIMEOUT_ATTEMPTS,
    DEFAULT_TASKS,
    DOWNLOAD_PART_EXTENSION,
    DOWNLOAD_QUALITIES,
    DOWNLOAD_REQUEST_HEADERS,
    DownloadMode,
    SubjectType,
)

SECRET_KEY_DEFAULT: str = (
    os.getenv("MOVIEBOX_SECRET_KEY_DEFAULT", "").strip()
    or "76iRl07s0xSN9jqmEWAt79EBJZulIQIsV64FZr2O"
)
SECRET_KEY_ALT: str = (
    os.getenv("MOVIEBOX_SECRET_KEY_ALT", "").strip()
    or "Xqn2nnO41/L92o1iuXhSLHTbXvY4Z5ZZ62m8mSLA"
)
AUTH_TOKEN: str | None = os.getenv("MOVIEBOX_AUTH_TOKEN", "").strip() or None


def _random_hex(length: int) -> str:
    return "".join(random.choices("0123456789abcdef", k=length))


def _random_gaid() -> str:
    return str(uuid.uuid4())


def _generate_client_info() -> tuple[str, str]:
    android_versions = [
        {"version": "9", "build": "PQ3A.190605.03081104"},
        {"version": "10", "build": "QP1A.191005.007.A3"},
        {"version": "11", "build": "RP1A.200720.011"},
        {"version": "12", "build": "S1B.220414.015"},
        {"version": "13", "build": "TQ2A.230405.003"},
    ]
    redmi_devices = [
        {"model": "23078RKD5C", "brand": "Redmi"},
        {"model": "2201117TY", "brand": "Redmi"},
        {"model": "2201117TG", "brand": "Redmi"},
        {"model": "22101316G", "brand": "Redmi"},
        {"model": "21121210G", "brand": "Redmi"},
        {"model": "M2012K11AG", "brand": "Redmi"},
        {"model": "M2007J20CG", "brand": "Redmi"},
    ]
    version_codes = [50020042, 50020043, 50020044, 50020045, 50020046]
    network_types = ["NETWORK_WIFI", "NETWORK_MOBILE"]
    timezones = [
        "Asia/Kolkata",
        "Asia/Shanghai",
        "Asia/Tokyo",
        "America/New_York",
        "Europe/London",
    ]

    android = random.choice(android_versions)
    device = random.choice(redmi_devices)
    version_code = random.choice(version_codes)
    network = random.choice(network_types)
    timezone = random.choice(timezones)
    gaid = _random_gaid()
    device_id = _random_hex(32)

    user_agent = (
        f"com.community.oneroom/{version_code} "
        f"(Linux; U; Android {android['version']}; en_US; "
        f"{device['model']}; Build/{android['build']}; Cronet/135.0.7012.3)"
    )
    client_info = (
        f'{{"package_name":"com.community.oneroom","version_name":"3.0.03.0529.03",'
        f'"version_code":{version_code},"os":"android","os_version":"{android["version"]}",'
        f'"install_ch":"ps","device_id":"{device_id}","install_store":"ps",'
        f'"gaid":"{gaid}","brand":"{device["brand"]}","model":"{device["model"]}",'
        f'"system_language":"en","net":"{network}","region":"US",'
        f'"timezone":"{timezone}","sp_code":"40401","X-Play-Mode":"2"}}'
    )
    return user_agent, client_info


USER_AGENT, CLIENT_INFO = _generate_client_info()

WEB_USER_AGENT: str = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36"
)
RETRY_STATUS_CODES: frozenset[int] = frozenset({
    403,
    407,
    429,
    500,
    502,
    503,
    504,
})
BLOCKED_HOST_KEYWORDS: tuple[str, ...] = (
    "fzmovies",
    "vegamovies",
    "effectivegate",
    "gatecpm",
    "adsterra",
    "doubleclick",
)
MEDIA_PATH_EXTENSIONS: tuple[str, ...] = (
    ".m3u8",
    ".mp4",
    ".mkv",
    ".webm",
    ".ts",
    ".mpd",
)
MEDIA_URL_HINTS: tuple[str, ...] = (
    ".m3u8",
    ".mp4",
    "downloadurl=",
    "resourcelink",
    "sign=",
    "/resource/",
)
SERIES_TRAILER_FRAGMENTS: tuple[str, ...] = (
    "/media/vone/",
    "-ld.mp4",
    "/trailer/",
)
TRAILER_CONTENT_FRAGMENTS: tuple[str, ...] = (
    "trailer",
    "teaser",
    "clip",
)
SIGNATURE_BODY_MAX_BYTES: int = 102_400
SEARCH_PER_PAGE_LIMIT = 20
RESULTS_PER_PAGE_AMOUNT = SEARCH_PER_PAGE_LIMIT

VALID_SUBJECT_ID_PATTERN = re.compile(r"^\d{18,20}$")


class TabID(StrEnum):
    ALL = "All"
    MUSIC = "Music"
    PEOPLE = "People"
    EDUCATION = "Education"
    MOVIE = "Movie"
    TV_SERIES = "TV"
    MOVIE_TV = "MovieTV"
    SHORT_TV = "ShortTV"


class TopicType(StrEnum):
    SUBJECT = "SUBJECT"
    VERTICAL_RANK = "VERTICAL_RANK"


class ResolutionType(IntEnum):
    _240P = 240
    _360P = 360
    _480P = 480
    _720P = 720
    _1080P = 1080
    _1440P = 1440
    _2160P = 2160
    _4320P = 4320
    UNSPECIFIED = 0


class CustomResolutionType(StrEnum):
    _240P = "240P"
    _360P = "360P"
    _480P = "480P"
    _720P = "720P"
    _1080P = "1080P"
    # below are currently not supported
    # _1440P = "1440p"
    # _2160P = "2160p"
    # _4320P = "4320p"
    BEST = "best"
    WORST = "worst"