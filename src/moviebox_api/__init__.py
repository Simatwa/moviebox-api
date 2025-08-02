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

from importlib import metadata
import logging

try:
    __version__ = metadata.version("moviebox-api")
except metadata.PackageNotFoundError:
    __version__ = "0.0.0"

__author__ = "Smartwa"
__repo__ = "https://github.com/Simatwa/moviebox-api"

logger = logging.getLogger(__name__)

from moviebox_api.core import Homepage, Search
from moviebox_api.requests import Session

from moviebox_api.download import (
    MediaFileDownloader,
    CaptionFileDownloader,
    DownloadableMovieFilesDetail,
    DownloadableSeriesFilesDetail,
    resolve_media_file_to_be_downloaded,
)
from moviebox_api.extra.movies import Auto

__all__ = [
    "Auto",
    "Homepage",
    "Search",
    "Session",
    "MediaFileDownloader",
    "CaptionFileDownloader",
    "DownloadableMovieFilesDetail",
    "DownloadableSeriesFilesDetail",
    "resolve_media_file_to_be_downloaded",
]
