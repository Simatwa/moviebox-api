"""Contains common functions for the submodule"""

from bs4 import BeautifulSoup


def souper(html: str) -> BeautifulSoup:
    """Convert html formatted txt to bts object

    Args:
        html (str): Html formatted text

    Returns:
        BeautifulSoup: Souped html
    """
    return BeautifulSoup(html, "html.parser")
