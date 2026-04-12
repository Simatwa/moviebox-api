<div align="center">

# moviebox-api

**Unofficial Python wrapper for Moviebox websites and Android app**  
Search, discover, download, and stream movies & TV series with subtitles

[![PyPI version](https://badge.fury.io/py/moviebox-api.svg)](https://pypi.org/project/moviebox-api)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/moviebox-api)](https://pypi.org/project/moviebox-api)
![Coverage](https://raw.githubusercontent.com/Simatwa/moviebox-api/refs/heads/main/assets/coverage.svg)
[![PyPI - License](https://img.shields.io/pypi/l/moviebox-api)](https://pypi.org/project/moviebox-api)
[![Downloads](https://pepy.tech/badge/moviebox-api)](https://pepy.tech/project/moviebox-api)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

[Features](#features) • [Installation](#installation) • [Quick Start](#quick-start) • [Usage](#usage) • [Documentation](https://moviebox-api-docs.netlify.app/)

</div>

## Features

* **Multi-Version Support** : Access multiple API versions (`v1`, `v2`, `v3`) for different provider services
* **Download Movies & TV Series** : High-quality downloads with multiple resolution options
* **Subtitle Support** : Download subtitles in multiple languages
* **Direct Streaming** : Stream via MPV or VLC without downloading (CLI only)
* **Faster Downloads** : Up to 5× faster than standard downloads
* **Async & Sync Support** : Fully asynchronous with synchronous fallback
* **Search & Discovery** : Find movies, trending content, and popular searches
* **Developer-Friendly** : Python API with Pydantic models

## Versions Available

There are currently three supported versions, each targeting a specific service of the provider (Moviebox):

1. **v1** – Primarily a web scraper with partial REST API interaction for `h5.aoneroom.com`
2. **v2** – A REST API client for `h5-api.aoneroom.com` - consumed by *moviebox.* such as moviebox.ph
3. **v3** – A REST API client for `api{3-6}.aoneroom.com` (Android app)

## Installation

### CLI (for end users)

```sh
pip install "moviebox-api[cli]"
```

### Base package (for developers)

```sh
pip install "moviebox-api"
```

### Termux (Android)

```sh
pip install moviebox-api --no-deps
pip install 'pydantic==2.9.2'
pip install rich click bs4 httpx throttlebuster
```

### Media Players (optional, required for streaming)

To stream content directly without downloading, install [MPV](https://mpv.io/installation) or [VLC](https://www.videolan.org):

<details>
<summary>Linux</summary>

```sh
# Ubuntu/Debian
sudo apt install mpv

# Fedora/RHEL
sudo dnf install mpv

# Arch Linux
sudo pacman -S mpv
```
</details>

<details>
<summary>macOS</summary>

```sh
brew install mpv
```
</details>

<details>
<summary>Windows</summary>

Download from [mpv.io/installation](https://mpv.io/installation/).
</details>

## Quick Start

### Command Line

```sh
# Download a movie
moviebox v2 download-movie "Avatar"

# Download a TV series episode
moviebox v2 download-series "Game of Thrones" -s 1 -e 1

# Stream a movie (requires MPV)
moviebox v2 download-movie "Avatar" --stream-via mpv
```

### Python API

```python
from moviebox_api.v1 import MovieAuto
import asyncio

async def main():
    auto = MovieAuto()
    movie_file, subtitle_file = await auto.run("Avatar")
    print(f"Movie: {movie_file.saved_to}")
    print(f"Subtitle: {subtitle_file.saved_to}")

asyncio.run(main())
```

## [Usage](https://moviebox-api-docs.netlify.app/)

This is just a brief usage information. For more details visit official docs - [https://moviebox-api-docs.netlify.app/](https://moviebox-api-docs.netlify.app/)

<details open>
<summary><h3>Command Line Interface</h3></summary>

```sh
moviebox v2 --help
```

| Command | Description |
|-|-|
| `download-movie` | Search, download, or stream movies, anime, music, and educational content |
| `download-series` | Search and download or stream TV series |
| `homepage-content` | Show contents displayed on the landing page |
| `item-details` | Show details of a particular movie or TV series |
| `mirror-hosts` | Discover available Moviebox mirror hosts |



#### Downloading Movies

**Basic usage:**
```sh
moviebox v2 download-movie "Avatar"
moviebox-v3 download-movie "avengers endgame" 
```

**Common options:**
```sh
moviebox v2 download-movie "Avatar" --quality 1080p
moviebox v2 download-movie "Avatar" --year 2009
moviebox v2 download-movie "Avatar" --dir ~/Movies
moviebox v2 download-movie "Avatar" --no-caption
moviebox v2 download-movie "Avatar" --yes
```

| Option | Description |
|-|-|
| `-y, --year` | Filter by release year |
| `-q, --quality` | Video quality: `best`, `1080p`, `720p`, `480p`, `360p`, `worst` |
| `-d, --dir` | Download directory |
| `-x, --language` | Subtitle language (default: English) |
| `--no-caption` | Skip subtitle download |
| `-Y, --yes` | Auto-confirm without prompts |

<details>
<summary>All options</summary>

```text
Usage: python -m moviebox_api v2 download-movie [OPTIONS] TITLE

  Search, download or stream items under movie/anime/music/education subject-types.

Options:
  -s, --subject-type [movies|education|music|anime]
                                  Subject type filter  [default: MOVIES]
  -y, --year INTEGER              Year filter  [default: 0]
  -q, --quality [worst|best|360p|480p|720p|1080p]
                                  Media quality  [default: BEST]
  -d, --dir DIRECTORY             Download directory
  -D, --caption-dir DIRECTORY     Caption download directory
  -m, --mode [start|resume|auto]  Download mode  [default: auto]
  -x, --language TEXT             Caption language  [default: English]
  -M, --movie-filename-tmpl TEXT  Movie filename template  [default: {title} ({release_year}).{ext}]
  -C, --caption-filename-tmpl TEXT
                                  Caption filename template  [default: {title} ({release_year}).{lan}.{ext}]
  -t, --tasks INTEGER RANGE       Parallel download tasks  [default: 5; 1<=x<=1000]
  -P, --part-dir DIRECTORY        Temporary parts directory
  -E, --part-extension TEXT       Part file extension  [default: .part]
  -N, --chunk-size INTEGER        Chunk size in kilobytes  [default: 256]
  -R, --timeout-retry-attempts INTEGER
                                  Retry attempts on timeout  [default: 10]
  -B, --merge-buffer-size INTEGER RANGE
                                  Merge buffer size in kilobytes  [1<=x<=102400]
  -X, --stream-via [mpv|vlc]      Stream via media player instead of downloading
  -c, --colour TEXT               Progress bar colour  [default: cyan]
  -U, --ascii                     Use unicode blocks for progress bar
  -z, --disable-progress-bar      Hide progress bar
  -I, --ignore-missing-caption    Continue download when caption is missing
  --leave / --no-leave            Keep progress bar leaves  [default: no-leave]
  --caption / --no-caption        Download caption  [default: caption]
  -O, --caption-only              Download caption only
  -S, --simple                    Show percentage and bar only
  -T, --test                      Test download without saving
  -V, --verbose                   Show detailed output
  -Q, --quiet                     Suppress interactive output
  -Y, --yes                       Skip confirmation prompt
  -h, --help                      Show this message and exit.
```
</details>

#### Downloading TV Series

**Basic usage:**
```sh
moviebox v2 download-series "Game of Thrones" -s 1 -e 1
moviebox-v3 download-series "A Knight of the Seven Kingdoms"
```

**Multiple episodes:**
```sh
# Download 5 episodes starting from S01E01
moviebox v2 download-series "Game of Thrones" -s 1 -e 1 -l 5

# Download entire season
moviebox v2 download-series "Game of Thrones" -s 1 -e 1 -l 100

# Download all remaining seasons
moviebox v2 download-series "Merlin" -s 1 -e 1 --auto-mode
```

| Option | Description |
|-|-|
| `-s, --season` | Season number (required) |
| `-e, --episode` | Starting episode number (required) |
| `-l, --limit` | Number of episodes to download (default: 1) |
| `-q, --quality` | Video quality |
| `-x, --language` | Subtitle language |
| `--no-caption` | Skip subtitles |
| `-Y, --yes` | Auto-confirm |
| `-A, --auto-mode` | Download all remaining seasons when `--limit` is 1 |

<details>
<summary>All options</summary>

```text
Usage: python -m moviebox_api v2 download-series [OPTIONS] TITLE

  Search and download or stream tv series.

Options:
  -y, --year INTEGER              Year filter  [default: 0]
  -s, --season INTEGER RANGE      Season number  [1<=x<=1000; required]
  -e, --episode INTEGER RANGE     Starting episode  [1<=x<=1000; required]
  -l, --limit INTEGER RANGE       Episodes to download  [default: 1; 1<=x<=1000]
  -q, --quality [worst|best|360p|480p|720p|1080p]
                                  Media quality  [default: BEST]
  -x, --language TEXT             Caption language  [default: English]
  -d, --dir DIRECTORY             Download directory
  -D, --caption-dir DIRECTORY     Caption download directory
  -m, --mode [start|resume|auto]  Download mode  [default: auto]
  -L, --episode-filename-tmpl TEXT
                                  Episode filename template  [default: {title} S{season}E{episode}.{ext}]
  -C, --caption-filename-tmpl TEXT
                                  Caption filename template  [default: {title} S{season}E{episode}.{lan}.{ext}]
  -t, --tasks INTEGER RANGE       Parallel download tasks  [default: 5; 1<=x<=1000]
  -P, --part-dir DIRECTORY        Temporary parts directory
  -f, --format [standard|group|struct]
                                  Episode organization format
  -E, --part-extension TEXT       Part file extension  [default: .part]
  -N, --chunk-size INTEGER        Chunk size in kilobytes  [default: 256]
  -R, --timeout-retry-attempts INTEGER
                                  Retry attempts on timeout  [default: 10]
  -B, --merge-buffer-size INTEGER RANGE
                                  Merge buffer size in kilobytes  [1<=x<=102400]
  -X, --stream-via [mpv|vlc]      Stream via media player instead of downloading
  -c, --colour TEXT               Progress bar colour  [default: cyan]
  -U, --ascii                     Use unicode blocks for progress bar
  -z, --disable-progress-bar      Hide progress bar
  -I, --ignore-missing-caption    Continue download when caption is missing
  --leave / --no-leave            Keep progress bar leaves  [default: no-leave]
  --caption / --no-caption        Download caption  [default: caption]
  -O, --caption-only              Download caption only
  -A, --auto-mode                 Download all remaining seasons when limit=1
  -S, --simple                    Show percentage and bar only
  -T, --test                      Test download without saving
  -V, --verbose                   Show detailed output
  -Q, --quiet                     Suppress interactive output
  -Y, --yes                       Skip confirmation prompt
  -h, --help                      Show this message and exit.
```
</details>



#### Streaming via Media Players

Stream content directly without downloading (requires MPV or VLC):

```sh
# Stream a movie
moviebox v2 download-movie "Avatar" --stream-via vlc

# Stream with subtitles in a specific language
moviebox v2 download-movie "Avatar" --stream-via mpv --language French

# Stream a series episode
moviebox v2 download-series "Game of Thrones" -s 1 -e 1 --stream-via vlc

# Stream with specific quality
moviebox v2 download-series "Breaking Bad" -s 1 -e 1 --stream-via vlc --quality 1080p
```

Streaming requires the `moviebox-api[cli]` installation and MPV or VLC installed on the system. Temporary files are cleaned up automatically.

### Command Shortcuts

```sh
# Full form
python -m moviebox_api v2 download-movie "Avatar"

# Short forms
movebox v2 download-movie "Avatar"
movebox-v2 download-movie "Avatar"
movebox-v1 download-movie "Avatar"
```

### Episode Organization

**Group format** — episodes organized into season subfolders:

```sh
moviebox v2 download-series Merlin -s 1 -e 1 --auto-mode --format group
```

```
Merlin (2009)/
  S1/
    Merlin S1E1.mp4
    Merlin S1E2.mp4
  S2/
    Merlin S2E1.mp4
```

**Struct format** — hierarchical directory structure using episode numbers as filenames:

```sh
moviebox v2 download-series Merlin -s 1 -e 1 --auto-mode --format struct
```

```
Merlin (2009)/
  S1/
    E1.mp4
    E2.mp4
  S2/
    E1.mp4
```

</details>

<details>
<summary><h3>Python API</h3></summary>

#### Simple Auto-Download

```python
from moviebox_api.v1 import MovieAuto
import asyncio

async def main():
    auto = MovieAuto()
    movie_file, subtitle_file = await auto.run("Avatar")
    print(f"Movie saved to: {movie_file.saved_to}")
    print(f"Subtitle saved to: {subtitle_file.saved_to}")

asyncio.run(main())
```

#### Download with Progress Tracking

```python
from moviebox_api.v1 import DownloadTracker, MovieAuto
import asyncio

async def progress_callback(progress: DownloadTracker):
    percent = (progress.downloaded_size / progress.expected_size) * 100
    print(f"[{percent:.2f}%] Downloading {progress.saved_to.name}", end="\r")

async def main():
    auto = MovieAuto(tasks=1)
    await auto.run("Avatar", progress_hook=progress_callback)

asyncio.run(main())
```

#### Download with Manual Confirmation

```python
from moviebox_api.v1.cli import Downloader
import asyncio

async def main():
    downloader = Downloader()
    movie_file, subtitle_files = await downloader.download_movie("Avatar")
    print(f"Downloaded: {movie_file}")
    print(f"Subtitles: {subtitle_files}")

asyncio.run(main())
```

#### Download TV Series Episodes

```python
from moviebox_api.v1.cli import Downloader
import asyncio

async def main():
    downloader = Downloader()
    episodes_map = await downloader.download_tv_series(
        "Merlin",
        season=1,
        episode=1,
        limit=2,
        # auto_mode=True  # Download entire remaining seasons when limit=1
    )
    print(f"Downloaded episodes: {episodes_map}")

asyncio.run(main())
```

#### Custom Configuration

```python
from moviebox_api.v1 import MovieAuto
import asyncio

async def main():
    auto = MovieAuto(
        caption_language="Spanish",
        quality="720p",
        download_dir="~/Downloads"
    )
    movie_file, subtitle_file = await auto.run("Avatar")

asyncio.run(main())
```

</details>

## Mirror Hosts

h5.aoneroom.com has ~~[multiple mirror hosts](https://github.com/Simatwa/moviebox-api/issues/27)~~. To use a specific mirror:

```sh
# v1
export MOVIEBOX_API_HOST="h5.aoneroom.com"

# v2
export MOVIEBOX_API_HOST_V2="h5-api.aoneroom.com"
```

Discover available mirrors:

```sh
moviebox v1 mirror-hosts
```

## Examples

- [V1 Examples](./docs/v1/examples/)
- [v2 Examples](./docs/v2/examples/)

## Contributors

<div align="center">

<a href="https://github.com/Simatwa/moviebox-api/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Simatwa/moviebox-api" />
</a>

</div>


<h2 align="center"> Disclaimer </h2>

> "All videos and pictures on MovieBox are from the Internet, and their copyrights belong to the original creators. We only provide webpage services and do not store, record, or upload any content."  
> — *moviebox.ph*

<div align=center>

**Long live Moviebox spirit.**
</div>

<div align="center">Made with ❤️ </div>