"""
### v1 - Web Scraper + Partial REST-API Client
**Endpoint:** `h5.aoneroom.com`

Operates against the H5 frontend of Moviebox. 
Combines HTML scraping with partial REST-API interaction, making it 
suitable for content discovery where structured API access is limited or 
inconsistent. Scraping logic handles page-rendered data not exposed via 
JSON endpoints.

- Approach: Hybrid (DOM scraping + REST)
- Target surface: H5 mobile web interface
- Use case: Content listing, metadata extraction from web-rendered pages
- Limitations: Susceptible to markup changes; partial API coverage only
"""

import logging

logger = logging.getLogger(__name__)

from throttlebuster import (  # noqa: E402
    DownloadedFile,
    DownloadMode,
    DownloadTracker,
)

from moviebox_api.v1.constants import (  # noqa: E402
    DOWNLOAD_QUALITIES,
    HOST_URL,
    MIRROR_HOSTS,
    SELECTED_HOST,
    SubjectType,
)
from moviebox_api.v1.core import (  # noqa: E402
    Homepage,
    HotMoviesAndTVSeries,
    MovieDetails,
    PopularSearch,
    Recommend,
    Search,
    SearchSuggestion,
    Trending,
    TVSeriesDetails,
)
from moviebox_api.v1.download import (  # noqa: E402
    CaptionFileDownloader,
    DownloadableMovieFilesDetail,
    DownloadableTVSeriesFilesDetail,
    MediaFileDownloader,
    resolve_media_file_to_be_downloaded,
)
from moviebox_api.v1.extras.auto import MovieAuto  # noqa: E402
from moviebox_api.v1.requests import Session  # noqa: E402

__all__ = [
    "Search",
    "Session",
    "Trending",
    "Homepage",
    "Recommend",
    "MovieAuto",
    "SubjectType",
    "MovieDetails",
    "PopularSearch",
    "TVSeriesDetails",
    "SearchSuggestion",
    "MediaFileDownloader",
    "HotMoviesAndTVSeries",
    "CaptionFileDownloader",
    "DownloadableMovieFilesDetail",
    "DownloadableTVSeriesFilesDetail",
    "resolve_media_file_to_be_downloaded",
    # Constants
    "DOWNLOAD_QUALITIES",
    "MIRROR_HOSTS",
    "SELECTED_HOST",
    "HOST_URL",
    "SubjectType",
    # Others
    "DownloadedFile",
    "DownloadMode",
    "DownloadTracker",
]
