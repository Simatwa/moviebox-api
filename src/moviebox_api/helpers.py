"""
This module provide functions for performing common and frequently required tasks
across the package.
"""

import re
import typing as t
from urllib.parse import urljoin

from moviebox_api import logger
from moviebox_api.constants import HOST_URL, ITEM_DETAILS_PATH
from moviebox_api.exceptions import UnsuccessfulResponseError

FILE_EXT_PATTERN = re.compile(r".+\.(\w+)\?.+")

ILLEGAL_CHARACTERS_PATTERN = re.compile(r"[^\w\-_\.\s()&|]")

VALID_ITEM_PAGE_URL_PATTERN = re.compile(r".*" + ITEM_DETAILS_PATH + r"/[\w-]+\?id\=\d{19,}.*")

SCHEME_HOST_PATTERN = re.compile(r"https?://[-_\.\w]+")


def get_absolute_url(relative_url: str) -> str:
    """Makes absolute url from relative one

    Args:
        relative_url (str): Path of a url

    Returns:
        str: Complete url with host
    """

    return urljoin(HOST_URL, re.sub(SCHEME_HOST_PATTERN, "", relative_url))


def assert_membership(value: t.Any, elements: t.Iterable, identity="Value"):
    """Asserts value is a member of elements

    Args:
        value (t.Any): member to be checked against.
        elements (t.Iterable): Iterables of members.
        identity (str, optional): Defaults to "Value".
    """
    assert value in elements, f"{identity} '{value}' is not one of {elements}"


def assert_instance(obj: object, class_or_tuple, name: str = "Parameter") -> t.NoReturn:
    """assert obj an instance of class_or_tuple"""

    assert isinstance(obj, class_or_tuple), (
        f"{name} value needs to be an instance of/any of {class_or_tuple} not {type(obj)}"
    )


def process_api_response(json: dict) -> dict | list:
    """Extracts the response data field

    Args:
        json (t.Dict): Whole server response

    Returns:
        t.Dict: Extracted data field value
    """
    if json.get("code", 1) == 0 and json.get("message") == "ok":
        return json["data"]

    logger.debug(f"Unsuccessful response received from server - {json}")
    raise UnsuccessfulResponseError(
        json,
        "Unsuccessful response from the server. Check `.response`  for detailed response info",
    )


extract_data_field_value = process_api_response


def get_filesize_string(size_in_bytes: int) -> str:
    """Get something like `343 MB` or `1.25 GB` depending on size_in_bytes."""
    units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    for unit in units:
        # 1024 or 1000 ?
        if size_in_bytes >= 1000.0:
            size_in_bytes /= 1000.0
        else:
            break
    return f"{size_in_bytes:.2f} {unit}"


def get_file_extension(url: str) -> str | None:
    """Extracts extension from file url e.g `mp4` or `srt`

    For example:
        url : https://valiw.hakunaymatata.com/resource/537977caa8c13703185d26471ce7de9f.mp4s?auth_key=1753024153-0-0-c824d3b5a5c8acc294bfd41de43c51ef"
        returns 'mp4'
    """
    all = re.findall(FILE_EXT_PATTERN, str(url))
    if all:
        return all[0]


def sanitize_filename(filename: str) -> str:
    """Remove illegal characters from a filename"""
    return re.sub(ILLEGAL_CHARACTERS_PATTERN, "", filename.replace(":", "-"))


def validate_item_page_url(url: str) -> str:
    """Checks whether specific item page url is valid"""
    finds = re.findall(VALID_ITEM_PAGE_URL_PATTERN, url)

    if finds:
        if finds[0] == url:
            return url

    raise ValueError(f"Invalid url for a specific item page - '{url}'")
