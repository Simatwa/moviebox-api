"""
This module provide functions for
performing common and frequently required tasks
as well as storing common variables required 
across the package
"""

from bs4 import BeautifulSoup as bts
from os import path
import typing as t
from typing import Dict
from moviebox_api.exceptions import UnsuccessfulResponse

mirror_hosts = ("httpx://moviebox.ng",)

site_url = mirror_hosts[0]


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
    if relative_url.startswith("/"):
        relative_url = relative_url[1:]
    return path.join(site_url, relative_url)


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


def process_api_response(json: Dict) -> Dict:
    """Extracts the response data field

    Args:
        json (Dict): Whole server response

    Returns:
        Dict: Extracted data field value
    """
    if json.get("code", 1) == 0 and json.get("message") == "ok":
        return json["data"]

    raise UnsuccessfulResponse(
        json,
        "Unsuccessful response from the server. Check `.response`  for response info",
    )


extract_data_field_value = process_api_response
