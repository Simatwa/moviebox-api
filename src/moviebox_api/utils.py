"""
This module provide functions & classes for
performing common and frequently required tasks
as well as storing common variables required
across the package
"""

from bs4 import BeautifulSoup as bts
import typing as t
from typing import Dict, List
from moviebox_api import logger
from moviebox_api.exceptions import UnsuccessfulResponseError
from urllib.parse import urljoin
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

selected_host = mirror_hosts[0]
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


def souper(contents: str) -> bts:
    """Converts str object to `soup`

    Args:
        contents (str): html formatted string

    Returns:
        bts: souped sring object
    """
    return bts(contents, "html.parser")


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
