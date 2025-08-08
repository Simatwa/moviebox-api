"""
This package allows you to download movies
and tv series from moviebox.ph and its mirror hosts.

Right from performing `search` query down to downloading
it in your desired quality.

For instance:

```python
from moviebox_api import Auto

async def main():
    auto = Auto()
    movie_saved_to, subtitle_saved_to = await auto.run("Avatar")
    print(movie_saved_to, subtitle_saved_to, sep="\n")
    # Output
    # /.../Avatar - 1080P.mp4
    # /.../Avatar - English.srt

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

```
"""

import logging
from importlib import metadata

try:
    __version__ = metadata.version("moviebox-api")
except metadata.PackageNotFoundError:
    __version__ = "0.0.0"

__author__ = "Smartwa"
__repo__ = "https://github.com/Simatwa/moviebox-api"

logger = logging.getLogger(__name__)

from moviebox_api.constants import (  # noqa: E402
    DOWNLOAD_QUALITIES,
    HOST_URL,
    MIRROR_HOSTS,
    SELECTED_HOST,
    SubjectType,
)
from moviebox_api.core import (  # noqa: E402
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
from moviebox_api.download import (  # noqa: E402
    CaptionFileDownloader,
    DownloadableMovieFilesDetail,
    DownloadableTVSeriesFilesDetail,
    MediaFileDownloader,
    resolve_media_file_to_be_downloaded,
)
from moviebox_api.extras.movies import Auto  # noqa: E402
from moviebox_api.requests import Session  # noqa: E402

__all__ = [
    "Auto",
    "Search",
    "Session",
    "Trending",
    "Homepage",
    "Recommend",
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
]
