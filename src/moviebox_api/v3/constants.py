"""
Constants for MovieBox API client.
"""
import os
import re
from enum import StrEnum

from moviebox_api.v1.constants import SubjectType

SECRET_KEY_DEFAULT: str = (
    os.getenv("MOVIEBOX_SECRET_KEY_DEFAULT", "").strip()
    or "76iRl07s0xSN9jqmEWAt79EBJZulIQIsV64FZr2O"
)
SECRET_KEY_ALT: str = (
    os.getenv("MOVIEBOX_SECRET_KEY_ALT", "").strip()
    or "Xqn2nnO41/L92o1iuXhSLHTbXvY4Z5ZZ62m8mSLA"
)
AUTH_TOKEN: str | None = os.getenv("MOVIEBOX_AUTH_TOKEN", "").strip() or None

USER_AGENT: str = (
    "com.community.oneroom/50020052 "
    "(Linux; U; Android 16; en_IN; sdk_gphone64_x86_64; "
    "Build/BP22.250325.006; Cronet/133.0.6876.3)"
)
CLIENT_INFO: str = (
    '{"package_name":"com.community.oneroom","version_name":"3.0.05.0711.03",'
    '"version_code":50020052,"os":"android","os_version":"16",'
    '"device_id":"da2b99c821e6ea023e4be55b54d5f7d8","install_store":"ps",'
    '"gaid":"d7578036d13336cc","brand":"google","model":"sdk_gphone64_x86_64",'
    '"system_language":"en","net":"NETWORK_WIFI","region":"IN",'
    '"timezone":"Asia/Calcutta","sp_code":""}'
)
WEB_USER_AGENT: str = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36"
)

RETRY_STATUS_CODES: frozenset[int] = frozenset(
    {
        403,
        407,
        429,
        500,
        502,
        503,
        504,
    }
)

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

# Series stream fragments that belong to trailers / promos, not episodes
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

# Body truncation for signing
SIGNATURE_BODY_MAX_BYTES: int = 102_400

SEARCH_PER_PAGE_LIMIT = 20

# Patterns


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


