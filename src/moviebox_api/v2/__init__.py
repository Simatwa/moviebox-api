"""
V2 of Moviebox-API
"""

import logging

logger = logging.getLogger(__name__)


logging.getLogger("moviebox_api.v1").setLevel(logging.DEBUG)

from moviebox_api.v2.core import (  # noqa: E402
    AnimeDetails,
    EducationDetails,
    Homepage,
    ItemDetails,
    MovieDetails,
    MusicDetails,
    Search,
    SearchSuggestion,
    SingleItemDetails,
    TVSeriesDetails,
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
    "TVSeriesDetails",
    "MovieDetails",
    "MusicDetails",
    "AnimeDetails",
    "EducationDetails",
]
