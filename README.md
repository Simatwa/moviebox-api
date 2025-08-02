<div align="center">

# moviebox-api
Unofficial wrapper for moviebox.ph - search, discover and download movies, tv-series and their subtitles.

[![PyPI version](https://badge.fury.io/py/moviebox-api.svg)](https://pypi.org/project/moviebox-api)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/moviebox-api)](https://pypi.org/project/moviebox-api)
[![PyPI - License](https://img.shields.io/pypi/l/moviebox-api)](https://pypi.org/project/moviebox-api)
[![Hits](https://hits.sh/github.com/Simatwa/moviebox-api.svg?label=Total%20hits&logo=dotenv)](https://github.com/Simatwa/moviebox-api "Total hits")
[![Code Coverage](https://img.shields.io/codecov/c/github/Simatwa/moviebox-api)](https://codecov.io/gh/Simatwa/moviebox-api)
[![Downloads](https://pepy.tech/badge/moviebox-api)](https://pepy.tech/project/moviebox-api)
<!-- TODO: Add logo & wakatime-->
</div>

## Features

- Search and discover movies and tv-series
- Download movies & tv-series and their subtitles
- Fully asynchronous
- Native pydantic modelling of response

## Installation

Run the following command in your terminal:

```sh
$ pip install "moviebox-api[cli]"

# For developers
$ pip install moviebox-api
```

## Usage

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
  download-movie   Search and download movie.
  download-series  Search and download tv series.
  mirror-hosts     Discover moviebox mirror hosts [env: MOVIEBOX_API_HOST]
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

```sh
$ python -m moviebox_api download-series <Series title> -s <season offset> -e <episode offset>
# e.g python -m moviebox_api download-series Avatar -s 1 -e 1
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

> [!NOTE]
> Moviebox.ph has several other mirror hosts, in order to set specific one to be used by the script simply expose it as environment variable using name `MOVIEBOX_API_HOST`. For instance, in Linux systems one might need to run `$ export MOVIEBOX_API_HOST="h5.aoneroom.com"`


## Disclaimer

> "All videos and pictures on MovieBox are from the Internet, and their copyrights belong to the original creators. We only provide webpage services and do not store, record, or upload any content." - moviebox.ph as on *Sunday 13th, July 2025*

> Long live Moviebox spirit

<p align="center"> Made with ❤️</p>