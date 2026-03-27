"""
Main module for the package.
Generate models from httpx request responses.
Also provides object mapping support to specific extracted item details
"""

import moviebox_api.v1.core
from moviebox_api.v2.helpers import get_absolute_url


class Homepage(moviebox_api.v1.core.Homepage):
    _url = get_absolute_url('/wefeed-h5api-bff/home?host=moviebox.ph')


class Search(moviebox_api.v1.core.Search):
    _url = get_absolute_url("/wefeed-h5api-bff/subject/search")


class SearchSuggestion(moviebox_api.v1.core.SearchSuggestion):
    _url = get_absolute_url("/wefeed-h5api-bff/subject/search-suggest")

