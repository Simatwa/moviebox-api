"""
This module provide functions for performing common and frequently required tasks
across the package.
"""

import json
import re
import typing as t
from urllib.parse import urljoin

import httpx

from moviebox_api.utils import get_event_loop
from moviebox_api.v1 import logger
from moviebox_api.v1.constants import HOST_URL, ITEM_DETAILS_PATH
from moviebox_api.v1.exceptions import UnsuccessfulResponseError

FILE_EXT_PATTERN = re.compile(r".+\.(\w+)\?.+")

ILLEGAL_CHARACTERS_PATTERN = re.compile(r"[^\w\-_\.\s()&|]")

VALID_ITEM_PAGE_URL_PATTERN = re.compile(
    r"^.*" + ITEM_DETAILS_PATH + r"/[\w-]+(?:\?id\=\d{17,}.*)?$"
)

SCHEME_HOST_PATTERN = re.compile(r"^https?://[-_\.\w]+$")

SERIES_NAME_WITH_SEASON_NUMBER_PATTERN = re.compile(r"^.*\sS\d{1,}$")

SERIES_NAME_WITH_SEASON_NUMBER_ONE_PATTERN = re.compile(r"^.*\sS1$")

UNWANTED_ITEM_NAME_PATTERN = re.compile(r"(\sS\d{1,}|\sS\d{1,}-S\d{1,}|-S\d{1,})")


def get_absolute_url(relative_url: str, base_url: str = HOST_URL) -> str:
    """Makes absolute url from relative one

    Args:
        relative_url (str): Path of a url

    Returns:
        str: Complete url with host
    """

    return urljoin(base_url, SCHEME_HOST_PATTERN.sub("", relative_url))


def assert_membership(value: t.Any, elements: t.Iterable, identity="Value"):
    """Asserts value is a member of elements

    Args:
        value (t.Any): member to be checked against.
        elements (t.Iterable): Iterables of members.
        identity (str, optional): Defaults to "Value".
    """
    assert value in elements, f"{identity} '{value}' is not one of {elements}"


def assert_instance(
    obj: object, class_or_tuple, name: str = "Parameter"
) -> t.NoReturn:
    """assert obj an instance of class_or_tuple"""

    assert isinstance(obj, class_or_tuple), (
        f"{name} value needs to be an instance of/any of {class_or_tuple} "
        f"not {type(obj)}"
    )


def process_api_response(response: httpx.Response) -> dict | list:
    """Extracts the response data field

    Args:
        response (t.Dict): Server response

    Returns:
        t.Dict: Extracted data field value
    """
    expected_content_type = "application/json"
    content_type = response.headers.get("content-type", "")

    if content_type != expected_content_type:
        raise RuntimeError(
            f"Unexpect content type {content_type!r} encountered. "
            f"Expected {expected_content_type!r} - BODY {response.text!r}"
        )

    j: dict = response.json()

    if j.get("code", 1) == 0 and j.get("message") == "ok":
        return j["data"]

    error_msg = (
        "Unsuccessful response received from server -"
        f"STATUS {response.status_code} - BODY: {response.text!r}"
    )

    logger.debug(error_msg)

    raise UnsuccessfulResponseError(
        response,
        error_msg,
    )


extract_data_field_value = process_api_response


def get_file_extension(url: str) -> str | None:
    """Extracts extension from file url e.g `mp4` or `srt`

    For example:
        url : https://valiw.hakunaymatata.com/resource/537977caa8c137031
        85d26471ce7de9f.mp4?auth_key=1753024153-0-0-c824d3b5a5c8acc294bfd41de43c51ef"
        returns 'mp4'
    """
    ext_match = FILE_EXT_PATTERN.match(str(url))

    if ext_match:
        return ext_match.groups()[0]


def validate_item_page_url(url: str) -> str:
    """Checks whether specific item page url is valid"""
    if VALID_ITEM_PAGE_URL_PATTERN.match(url):
        return url

    raise ValueError(f"Invalid url for a specific item page - '{url}'")


def is_valid_search_item(item_name: str) -> bool:
    if SERIES_NAME_WITH_SEASON_NUMBER_PATTERN.match(item_name):
        if SERIES_NAME_WITH_SEASON_NUMBER_ONE_PATTERN.match(item_name):
            return True

        return False

    return True


def sanitize_item_name(item_name: str) -> str:
    return UNWANTED_ITEM_NAME_PATTERN.sub("", item_name)
