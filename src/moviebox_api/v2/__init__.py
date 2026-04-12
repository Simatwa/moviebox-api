"""
### v2 - Pure REST-API Client
**Endpoint:** `h5-api.aoneroom.com`

Targets the dedicated REST-API backend powering the H5 web interfaces 
- moviebox.ph, moviebox.pk, videodownloader.site etc (https://github.com/Simatwa
/moviebox-api/issues/27). 

Eliminates scraping entirely in favor of structured 
JSON request/response cycles. 

Provides more stable and predictable data access compared to v1.

- Approach: Pure REST-API
- Target surface: H5 API backend
- Use case: Structured content queries, metadata retrieval, stream resolution
- Advantages over v1: No markup dependency; cleaner response parsing; more reliable
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
