<div align="center">

# moviebox-api
Unofficial wrapper for moviebox.ph - search, discover and download movies, tv-series and their subtitles.

[![PyPI version](https://badge.fury.io/py/moviebox-api.svg)](https://pypi.org/project/moviebox-api)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/moviebox-api)](https://pypi.org/project/moviebox-api)
![Coverage](https://raw.githubusercontent.com/Simatwa/moviebox-api/refs/heads/main/assets/coverage.svg)
[![PyPI - License](https://img.shields.io/pypi/l/moviebox-api)](https://pypi.org/project/moviebox-api)
[![Downloads](https://pepy.tech/badge/moviebox-api)](https://pepy.tech/project/moviebox-api)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
</div>

## Features

- Search & download movies, tv-series and their subtitles.
- Native pydantic modelling of responses
- Fully asynchronous with synchronous support for major operations

## Installation

Run the following command in your terminal:

```sh
$ pip install "moviebox-api[cli]"

# For developers
$ pip install moviebox-api

```

<details>

<summary>

### Termux 

</summary>

```sh
pip install moviebox-api --no-deps
pip install 'pydantic==2.9.2'
pip install rich click bs4 httpx throttlebuster
```
</details>

## Usage

<details open>

<summary>

### Developers

</summary>

```python
from moviebox_api import MovieAuto

async def main():
    auto = MovieAuto()
    movie_file, subtitle_file = await auto.run("Avatar")
    print(movie_file.saved_to, subtitle_file.saved_to, sep="\n")
    # Output
    # /.../Avatar - 1080P.mp4
    # /.../Avatar - English.srt

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
```

Perform download with progress hook

```python
from moviebox_api import DownloadTracker, MovieAuto


async def callback_function(progress: DownloadTracker):
    percent = (progress.downloaded_size / progress.expected_size) * 100

    print(f">>[{percent:.2f}%] Downloading {progress.saved_to.name}", end="\r")


if __name__ == "__main__":
    import asyncio

    auto = MovieAuto(caption_language=None)
    asyncio.run(auto.run(query="Avatar", progress_hook=callback_function))
```



#### More Control

Prompt for item confirmation prior to download

##### Movie

```python
# $ pip install 'moviebox-api[cli]'

from moviebox_api.cli import Downloader


async def main():
    downloader = Downloader()
    movie_file, subtitle_files = await downloader.download_movie(
        "avatar",
    )
    print(movie_file, subtitle_files, sep="\n")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
```

##### TV-Series

```python
# $ pip install 'moviebox-api[cli]'

from moviebox_api.cli import Downloader

async def main():
    downloader = Downloader()
    episodes_content_map = await downloader.download_tv_series(
        "Merlin",
        season=1,
        episode=1,
        limit=2,
        # limit=13 # This will download entire 13 episodes of season 1
    )

    print(episodes_content_map)

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
```

For more details youn can go through the [full documentation](./docs/README.md)

</details>


<details>

<summary>

### Commandline

```sh
# $ python -m moviebox_api --help

Usage: moviebox [OPTIONS] COMMAND [ARGS]...

  Search and download movies/tv-series and their subtitles. envvar-prefix :
  MOVIEBOX

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  download-movie    Search and download movie.
  download-series   Search and download tv series.
  homepage-content  Show contents displayed at landing page
  item-details      Show details of a particular movie/tv-series
  mirror-hosts      Discover Moviebox mirror hosts [env: MOVIEBOX_API_HOST]
  popular-search    Movies/tv-series many people are searching now
```

</summary>

<details>

<summary>

#### Download Movie

```sh
$ python -m moviebox_api download-movie <Movie title>
# e.g python -m moviebox_api download-movie Avatar
```

</summary>

```sh
# python -m moviebox_api download-movie --help

Usage: moviebox download-movie [OPTIONS] TITLE

  Search and download movie.

Options:
  -y, --year INTEGER              Year filter for the movie to proceed with
                                  [default: 0]
  -q, --quality [worst|best|360p|480p|720p|1080p]
                                  Media quality to be downloaded  [default:
                                  BEST]
  -d, --dir DIRECTORY             Directory for saving the movie to  [default:
                                  /home/smartwa/git/smartwa/moviebox-api]
  -D, --caption-dir DIRECTORY     Directory for saving the caption file to
                                  [default:
                                  /home/smartwa/git/smartwa/moviebox-api]
  -m, --mode [start|resume|auto]  Start the download, resume or set
                                  automatically  [default: auto]
  -x, --language TEXT             Caption language filter  [default: English]
  -M, --movie-filename-tmpl TEXT  Template for generating movie filename
                                  [default: %(title)s (%(release_year)d) -
                                  %(resolution)dP.%(ext)s]
  -C, --caption-filename-tmpl TEXT
                                  Template for generating caption filename
                                  [default: %(title)s (%(release_year)d) -
                                  %(lanName)s.%(ext)s]
  -t, --tasks INTEGER RANGE       Number of tasks to carry out the download
                                  [default: 2; 1<=x<=1000]
  -P, --part-dir DIRECTORY        Directory for temporarily saving the
                                  downloaded file-parts to  [default:
                                  /home/smartwa/git/smartwa/moviebox-api]
  -E, --part-extension TEXT       Filename extension for download parts
                                  [default: .part]
  -N, --chunk-size INTEGER        Streaming download chunk size in kilobytes
                                  [default: 256]
  -B, --merge-buffer-size INTEGER RANGE
                                  Buffer size for merging the separated files
                                  in kilobytes [default : CHUNK_SIZE]
                                  [1<=x<=102400]
  -c, --colour TEXT               Progress bar display colour  [default: cyan]
  -A, --ascii                     Use unicode (smooth blocks) to fill the
                                  progress-bar meter
  -z, --disable-progress-bar      Do not show download progress-bar
  --leave / --no-leave            Keep all leaves of the progress-bar
                                  [default: no-leave]
  --caption / --no-caption        Download caption file  [default: caption]
  -O, --caption-only              Download caption file only and ignore movie
  -S, --simple                    Show download percentage and bar only in
                                  progressbar
  -T, --test                      Just test if download is possible but do not
                                  actually download
  -V, --verbose                   Show more detailed interactive texts
  -Q, --quiet                     Disable showing interactive texts on the
                                  progress (logs)
  -Y, --yes                       Do not prompt for movie confirmation
  -h, --help                      Show this message and exit.
```

</details>

<details>

<summary>

#### Download Series

```sh
$ python -m moviebox_api download-series <Series title> -s <season number> -e <episode number>
# e.g python -m moviebox_api download-series Merlin -s 1 -e 1
```

</summary>

```sh
# python -m moviebox_api download-series --help

Usage: moviebox download-series [OPTIONS] TITLE

  Search and download tv series.

Options:
  -y, --year INTEGER              Year filter for the series to proceed with :
                                  0  [default: 0]
  -s, --season INTEGER RANGE      TV Series season filter  [1<=x<=1000;
                                  required]
  -e, --episode INTEGER RANGE     Episode offset of the tv-series season
                                  [1<=x<=1000; required]
  -l, --limit INTEGER RANGE       Total number of episodes to download in the
                                  season  [default: 1; 1<=x<=1000]
  -q, --quality [worst|best|360p|480p|720p|1080p]
                                  Media quality to be downloaded  [default:
                                  BEST]
  -x, --language TEXT             Caption language filter  [default: English]
  -d, --dir DIRECTORY             Directory for saving the series file to
                                  [default:
                                  /home/smartwa/git/smartwa/moviebox-api]
  -D, --caption-dir DIRECTORY     Directory for saving the caption file to
                                  [default:
                                  /home/smartwa/git/smartwa/moviebox-api]
  -m, --mode [start|resume|auto]  Start new download, resume or set
                                  automatically  [default: auto]
  -L, --episode-filename-tmpl TEXT
                                  Template for generating series episode
                                  filename  [default: %(title)s
                                  S%(season)dE%(episode)d -
                                  %(resolution)dP.%(ext)s]
  -C, --caption-filename-tmpl TEXT
                                  Template for generating caption filename
                                  [default: %(title)s S%(season)dE%(episode)d
                                  - %(lanName)s.%(ext)s]
  -t, --tasks INTEGER RANGE       Number of tasks to carry out the download
                                  [default: 2; 1<=x<=1000]
  -P, --part-dir DIRECTORY        Directory for temporarily saving the
                                  downloaded file-parts to  [default:
                                  /home/smartwa/git/smartwa/moviebox-api]
  -E, --part-extension TEXT       Filename extension for download parts
                                  [default: .part]
  -N, --chunk-size INTEGER        Streaming download chunk size in kilobytes
                                  [default: 256]
  -B, --merge-buffer-size INTEGER RANGE
                                  Buffer size for merging the separated files
                                  in kilobytes [default : CHUNK_SIZE]
                                  [1<=x<=102400]
  -c, --colour TEXT               Progress bar display color  [default: cyan]
  -A, --ascii                     Use unicode (smooth blocks) to fill the
                                  progress-bar meter
  -z, --disable-progress-bar      Do not show download progress-bar
  --leave / --no-leave            Keep all leaves of the progressbar
                                  [default: no-leave]
  --caption / --no-caption        Download caption file  [default: caption]
  -O, --caption-only              Download caption file only and ignore movie
  -S, --simple                    Show download percentage and bar only in
                                  progressbar
  -T, --test                      Just test if download is possible but do not
                                  actually download
  -V, --verbose                   Show more detailed interactive texts
  -Q, --quiet                     Disable showing interactive texts on the
                                  progress (logs)
  -Y, --yes                       Do not prompt for tv-series confirmation
  -h, --help                      Show this message and exit.
```

</details>

</details>

## Further info

> [!TIP]
> Shorthand for `$ python -m moviebox_api` is simply `$ moviebox`

**Moviebox.ph** has [several other mirror hosts](https://github.com/Simatwa/moviebox-api/issues/27), in order to set specific one to be used by the script simply expose it as environment variable using name `MOVIEBOX_API_HOST`. For instance, in Linux systems one might need to run `$ export MOVIEBOX_API_HOST="h5.aoneroom.com"`


## Disclaimer

> "All videos and pictures on MovieBox are from the Internet, and their copyrights belong to the original creators. We only provide webpage services and do not store, record, or upload any content." - moviebox.ph as on *Sunday 13th, July 2025*

Long live Moviebox spirit.

<p align="center"> Made with ❤️</p>