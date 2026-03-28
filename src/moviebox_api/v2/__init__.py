"""
v2 of the Moviebox-API

Required:

1. Core - link models with services
2. Models  - data schema
3. Services - fetch data from server
"""

import logging

logger = logging.getLogger(__name__)


logging.getLogger("moviebox_api.v1").setLevel(logging.DEBUG)

from moviebox_api.v2.core import (  # noqa: E402
    Homepage,
    ItemDetails,
    Search,
    SearchSuggestion,
    SingleItemDetails,
    TVSeriesItemDetails,
)
from moviebox_api.v2.download import (  # noqa: E402
    DownloadableSingleFilesDetail,
    DownloadableTVSeriesFilesDetail,
)
from moviebox_api.v2.requests import Session  # noqa: E402

__all__ = [
    "Session",
    "DownloadableSingleFilesDetail",
    "DownloadableTVSeriesFilesDetail",
    "DownloadableSingleFilesDetail",
    "DownloadableTVSeriesFilesDetail",
    "Homepage",
    "ItemDetails",
    "Search",
    "SearchSuggestion",
    "SingleItemDetails",
    "TVSeriesItemDetails",
]
