"""
This module provide functions for
performing common and frequently required tasks
across the package.
"""

import re

# from bs4 import BeautifulSoup as bts
import typing as t
from typing import Dict, List
from moviebox_api import logger
from moviebox_api.exceptions import UnsuccessfulResponseError
from moviebox_api.constants import host_url
from urllib.parse import urljoin

file_ext_pattern = re.compile(r".+\.(\w+)\?.+")

# Not needed currently
''' 
def souper(contents: str) -> bts:
    """Converts str object to `soup`

    Args:
        contents (str): html formatted string

    Returns:
        bts: souped sring object
    """
    return bts(contents, "html.parser")
'''


def get_absolute_url(relative_url: str) -> str:
    """Makes absolute url from relative url

    Args:
        relative_url (str): Incomplete url

    Returns:
        str: Complete url with host
    """
    return urljoin(host_url, relative_url)


def assert_membership(value: t.Any, elements: t.Iterable, identity="Value"):
    """Asserts value is a member of elements

    Args:
        value (t.Any): member to be checked against.
        elements (t.Iterable): Iterables of members.
        identity (str, optional):. Defaults to "Value".
    """
    assert value in elements, f"{identity} '{value}' is not one of {elements}"


def assert_instance(obj: object, class_or_tuple, name: str = "Parameter"):
    """assert obj an instance of class_or_tuple"""
    assert isinstance(
        obj, class_or_tuple
    ), f"{name} value needs to be an instace of {class_or_tuple} not {type(obj)}"


def process_api_response(json: Dict) -> Dict | List:
    """Extracts the response data field

    Args:
        json (Dict): Whole server response

    Returns:
        Dict: Extracted data field value
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
    """Get something like 343 MB or 1.25 GB depending on size_in_bytes."""
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
        returns mp4
    """
    all = re.findall(file_ext_pattern, str(url))
    if all:
        return all[0]
