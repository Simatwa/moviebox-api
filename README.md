<div align="center">

# moviebox-api
Unofficial wrapper for moviebox.ph - search, discover and download movies, tv-series and their subtitles.

[![PyPI version](https://badge.fury.io/py/moviebox-api.svg)](https://pypi.org/project/moviebox-api)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/moviebox-api)](https://pypi.org/project/moviebox-api)
[![PyPI - License](https://img.shields.io/pypi/l/moviebox-api)](https://pypi.org/project/moviebox-api)
[![Hits](https://hits.sh/github.com/Almas-Ali/moviebox-api.svg?label=Total%20hits&logo=dotenv)](https://github.com/Almas-Ali/moviebox-api "Total hits")
[![Code Coverage](https://img.shields.io/codecov/c/github/Almas-Ali/moviebox-api)](https://codecov.io/gh/Almas-Ali/moviebox-api)
[![Downloads](https://pepy.tech/badge/moviebox-api)](https://pepy.tech/project/moviebox-api)
<!-- TODO: Add logo & wakatime-->
</div>

## Features

- Search and discover movies and tv-series
- Download movies & tv-series and their subtitles
- Fully asynchronous
- Native pydantic modelling of response

<details open>

<summary>

## Developers

</summary>

```python
from moviebox_api import Auto

async def main():
    auto = Auto()
    movie_saved_to, subtitle_saved_to = await auto.run("Avatar")
    print(movie_saved_to, subtitle_saved_to, sep="\n")
    # Output
    # /home/smartwa/.../Avatar - 1080P.mp4
    # /home/smartwa/.../Avatar - English.srt

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

```


</details>


<details>

<summary>

## Commandline

```sh
# $ python -m moviebox_api --help


Usage: python -m moviebox_api [OPTIONS] COMMAND [ARGS]...

  Search and download movies/series and their subtitles

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  download-movie   Search and download movie.
  download-series  Search and download tv series.

```

</summary>

<details>

<summary>

### Download Movie

```sh
$ python -m moviebox_api download-movie <Movie title>
# e.g python -m moviebox_api download-movie Avatar
```

</summary>

```sh
# python -m moviebox_api download-movie --help

Usage: python -m moviebox_api download-movie [OPTIONS] TITLE

  Search and download movie.

Options:
  -q [WORST|BEST|360P|480P|720P|1080P]
                                  Media quality to be downloaded : BEST
  -d, --directory DIRECTORY       Directory for saving the movie to : PWD
  -x, --language TEXT             Subtitle language filter
  --caption / --no-caption        Download caption file. : True
  --caption-only                  Download caption file only and ignore movie
                                  : False
  -y, --yes                       Do not prompt for movie confirmation : False
  -h, --help                      Show this message and exit.

```

</details>

<details>

<summary>

### Download Series

```sh
$ python -m moviebox_api download-series <Series title> -s <season offset> -e <episode offset>
# e.g python -m moviebox_api download-movie Avatar -s 1 -e 1
```

</summary>

```sh
# python -m moviebox_api download-movie --help


Usage: python -m moviebox_api download-series [OPTIONS] TITLE

  Search and download tv series.

Options:
  -s, --season INTEGER RANGE      TV Series season filter  [1<=x<=1000;
                                  required]
  -e, --episode INTEGER RANGE     Episode offset of the tv-series season
                                  [1<=x<=1000; required]
  -l, --limit INTEGER RANGE       Total number of episodes to download in the
                                  season : 1  [1<=x<=1000]
  -q [WORST|BEST|360P|480P|720P|1080P]
                                  Media quality to be downloaded : BEST
  -d, --directory DIRECTORY       Directory for saving the movie to : PWD
  -x, --language TEXT             Subtitle language filter : English
  --caption / --no-caption        Download caption file : True
  --caption-only                  Download caption file only and ignore series
                                  : False
  -y, --yes                       Do not prompt for tv-series confirmation :
                                  False
  -h, --help                      Show this message and exit.

```

<details>

<summary>



</summary>

</details>

</details>
</details>

# Disclaimer

> "All videos and pictures on MovieBox are from the Internet, and their copyrights belong to the original creators. We only provide webpage services and do not store, record, or upload any content." - Moviebox as on *Sunday 13th, July 2025*

Long live Moviebox spirit

<p align="center"> Made with ❤️</p>