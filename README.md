<div align="center">

# moviebox-api
Unofficial wrapper for moviebox.ph - search, discover and download movies, tv-series and their subtitles.

[![PyPI version](https://badge.fury.io/py/moviebox-api.svg)](https://pypi.org/project/moviebox-api)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/moviebox-api)](https://pypi.org/project/moviebox-api)
[![PyPI - License](https://img.shields.io/pypi/l/moviebox-api)](https://pypi.org/project/moviebox-api)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Hits](https://hits.sh/github.com/Simatwa/moviebox-api.svg?label=Total%20hits&logo=dotenv)](https://github.com/Simatwa/moviebox-api "Total hits")
[![Downloads](https://pepy.tech/badge/moviebox-api)](https://pepy.tech/project/moviebox-api)
<!-- 
[![Code Coverage](https://img.shields.io/codecov/c/github/Simatwa/moviebox-api)](https://codecov.io/gh/Simatwa/moviebox-api)
-->
<!-- TODO: Add logo & wakatime-->
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
pip install rich click httpx tqdm bs4
```
</details>

## Usage

> [!NOTE]
> Much focus right now is on implementing more features. The docs will be updated as time goes by. Otherwise, I cannot document this any better than the code itself, so take a look at [moviebox_api](src/moviebox_api/) package or its [tests](tests).

<details open>

<summary>

### Developers

</summary>

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

Perform download with progress hook

```python
from moviebox_api import Auto

async def callback_function(progress: dict):
    percent = (progress["downloaded_size"] / progress["size"]) * 100

    print(f">>[{percent:.2f}%] Downloading {progress["filename"]}", end="\r")

if __name__=="__main__":
    import asyncio

    auto = Auto(caption_language=None)
    asyncio.run(
        auto.run(
            query="Avatar",
            progress_hook=callback_function,
            progress_bar=False
            )
        )
```



#### More Control

Prompt for item confirmation prior to download

##### Movie

```python
# $ pip install 'moviebox-api[cli]'

from moviebox_api.cli import Downloader

async def main():
    downloader = Downloader()
    movie_path, subtitle_path = await downloader.download_movie("avatar")
    print(movie_path, subtitle_path, sep="\n")

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
```

##### TV-Series

```python
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

    # output
```

```json
    {
      1: {
        "captions_path" : ["/..S1E1 - english.srt"],
        "movie_path" : "/..S1E1.mp4",
      },
      2: {
        "captions_path" : ["/..S1E1 - english.srt"],
        "movie_path" : "/..S1E2.mp4",
      }
    }
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
  mirror-hosts      Discover Moviebox mirror hosts [env: MOVIEBOX_API_HOST]
  popular-search    Movies/tv-series many people are searching now
```

</summary>

<details>

<summary>

#### Download Movie

```
$ python -m moviebox_api download-movie <Movie title>
# e.g python -m moviebox_api download-movie Avatar
```

</summary>

```sh
# python -m moviebox_api download-movie --help

Usage: moviebox download-movie [OPTIONS] TITLE

  Search and download movie.

Options:
  -y, --year INTEGER              Year filter for the movie to proceed with :
                                  0
  -q, --quality [worst|best|360p|480p|720p|1080p]
                                  Media quality to be downloaded : BEST
  -d, --dir DIRECTORY             Directory for saving the movie to : PWD
  -D, --caption-dir DIRECTORY     Directory for saving the caption file to :
                                  PWD
  -Z, --chunk-size INTEGER RANGE  Chunk-size for downloading files in KB : 512
                                  [1<=x<=10000]
  -m, --mode [start|resume|auto]  Start the download, resume or set
                                  automatically : AUTO
  -c, --colour TEXT               Progress bar display colour : cyan
  -A, --ascii                     Use unicode (smooth blocks) to fill the
                                  progress-bar meter : False
  -x, --language TEXT             Caption language filter : [English]
  -M, --movie-filename-tmpl TEXT  Template for generating movie filename :
                                  [default]
  -C, --caption-filename-tmpl TEXT
                                  Template for generating caption filename :
                                  [default]
  --progress-bar / --no-progress-bar
                                  Display or disable progress-bar : True
  --leave / --no-leave            Keep all leaves of the progressbar : True
  --caption / --no-caption        Download caption file : True
  -O, --caption-only              Download caption file only and ignore movie
                                  : False
  -S, --simple                    Show download percentage and bar only in
                                  progressbar : False
  -T, --test                      Just test if download is possible but do not
                                  actually download : False
  -V, --verbose                   Show more detailed interactive texts : False
  -Q, --quiet                     Disable showing interactive texts on the
                                  progress (logs) : False
  -Y, --yes                       Do not prompt for movie confirmation : False
  -h, --help                      Show this message and exit.

```

</details>

<details>

<summary>

#### Download Series

```
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
                                  0
  -s, --season INTEGER RANGE      TV Series season filter  [1<=x<=1000;
                                  required]
  -e, --episode INTEGER RANGE     Episode offset of the tv-series season
                                  [1<=x<=1000; required]
  -l, --limit INTEGER RANGE       Total number of episodes to download in the
                                  season : 1  [1<=x<=1000]
  -q, --quality [worst|best|360p|480p|720p|1080p]
                                  Media quality to be downloaded : BEST
  -x, --language TEXT             Caption language filter : [English]
  -d, --dir DIRECTORY             Directory for saving the series file to :
                                  PWD
  -D, --caption-dir DIRECTORY     Directory for saving the caption file to :
                                  PWD
  -Z, --chunk-size INTEGER RANGE  Chunk-size for downloading files in KB : 512
                                  [1<=x<=10000]
  -m, --mode [start|resume|auto]  Start new download, resume or set
                                  automatically : AUTO
  -E, --episode-filename-tmpl TEXT
                                  Template for generating series episode
                                  filename : [default]
  -C, --caption-filename-tmpl TEXT
                                  Template for generating caption filename :
                                  [default]
  -c, --colour TEXT               Progress bar display color : cyan
  -A, --ascii                     Use unicode (smooth blocks) to fill the
                                  progress-bar meter : False
  --progress-bar / --no-progress-bar
                                  Display or disable progress-bar : True
  --leave / --no-leave            Keep all leaves of the progressbar : True
  --caption / --no-caption        Download caption file : True
  -O, --caption-only              Download caption file only and ignore movie
                                  : False
  -S, --simple                    Show download percentage and bar only in
                                  progressbar : False
  -T, --test                      Just test if download is possible but do not
                                  actually download : False
  -V, --verbose                   Show more detailed interactive texts : False
  -Q, --quiet                     Disable showing interactive texts on the
                                  progress (logs) : False
  -Y, --yes                       Do not prompt for tv-series confirmation :
                                  False
  -h, --help                      Show this message and exit.

```

</details>

</details>

## Further info

> [!TIP]
> Shorthand for `$ python -m moviebox_api` is simply `$ moviebox`

**Moviebox.ph** has several other mirror hosts, in order to set specific one to be used by the script simply expose it as environment variable using name `MOVIEBOX_API_HOST`. For instance, in Linux systems one might need to run `$ export MOVIEBOX_API_HOST="h5.aoneroom.com"`


## Disclaimer

> "All videos and pictures on MovieBox are from the Internet, and their copyrights belong to the original creators. We only provide webpage services and do not store, record, or upload any content." - moviebox.ph as on *Sunday 13th, July 2025*

Long live Moviebox spirit

<p align="center"> Made with ❤️</p>