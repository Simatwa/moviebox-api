<div align="center">

# moviebox-api

**Unofficial Python wrapper for moviebox.ph**  
Search, discover, download, and stream movies & TV series with subtitles

[![PyPI version](https://badge.fury.io/py/moviebox-api.svg)](https://pypi.org/project/moviebox-api)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/moviebox-api)](https://pypi.org/project/moviebox-api)
![Coverage](https://raw.githubusercontent.com/Simatwa/moviebox-api/refs/heads/main/assets/coverage.svg)
[![PyPI - License](https://img.shields.io/pypi/l/moviebox-api)](https://pypi.org/project/moviebox-api)
[![Downloads](https://pepy.tech/badge/moviebox-api)](https://pepy.tech/project/moviebox-api)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Usage](#-usage) • [Documentation](#-documentation)

</div>



## 📋 Table of Contents

- [✨ Features](#-features)
- [📦 Installation](#-installation)
  - [For Users (CLI)](#for-users-cli)
  - [For Developers](#for-developers)
  - [Media Player (Optional)](#media-players-optional-for-streaming)
  - [Termux Support](#termux-support)
- [🚀 Quick Start](#-quick-start)
  - [Interactive Menu (Easiest)](#interactive-menu-easiest)
  - [Command Line](#command-line-examples)
  - [Python API](#python-api-example)
- [📖 Usage](#-usage)
  - [🖥️ Command Line Interface](#️-command-line-interface)
  - [🐍 Python API](#-python-api)
- [📚 Documentation](#-documentation)
- [⚙️ Advanced Configuration](#️-advanced-configuration)
- [⚠️ Disclaimer](#️-disclaimer)



## ✨ Features

- 🎬 **Download Movies & TV Series** - High-quality downloads with multiple resolution options
- 📝 **Subtitle Support** - Download subtitles in multiple languages
- 🎥 **Stream with MPV or VLC** - Watch directly without downloading (CLI only)
- ⚡ **Super Fast Downloads** - Over 5x faster than standard downloads
- 🔄 **Async & Sync Support** - Fully asynchronous with synchronous fallback
- 🎯 **Interactive Menu** - User-friendly TUI for easy navigation
- 🔍 **Search & Discovery** - Find movies, trending content, and popular searches
- 🛠️ **Developer-Friendly** - Clean Python API with Pydantic models 




## 📦 Installation

### For Users (CLI)

Install with command-line interface support:

```sh
pip install "moviebox-api[cli]"
```

### For Developers

Install base package for Python integration:

```sh
pip install moviebox-api
```

### Media Players (Optional, for Streaming)

To stream content directly without downloading, install [MPV](https://mpv.io/installation) or [VLC](https://www.videolan.org) media players:

<details>
<summary><b>Linux</b></summary>

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
<summary><b>macOS</b></summary>

```sh
# Using Homebrew
brew install mpv
```
</details>

<details>
<summary><b>Windows</b></summary>

Download from [mpv.io/installation](https://mpv.io/installation/)
</details>

### Termux Support

<details>
<summary>Installation for Termux (Android)</summary>

```sh
pip install moviebox-api --no-deps
pip install 'pydantic==2.9.2'
pip install rich click bs4 httpx throttlebuster
```
</details>



## 🚀 Quick Start

### Interactive Menu (Easiest)

Launch the interactive menu for a user-friendly experience:

```sh
moviebox-interactive
```

Or:

```sh
moviebox interactive
```

The interactive menu provides:
- 🎬 Download Movies
- 📺 Download TV Series  
- 🎥 Stream Movies with MPV/VLC
- 📡 Stream TV Series with MPV/VLC
- 🔍 Discover & Search Content

### Command Line Examples

**Download a movie:**
```sh
moviebox download-movie "Avatar"
```

**Download a TV series episode:**
```sh
moviebox download-series "Game of Thrones" -s 1 -e 1
```

**Stream a movie (requires MPV):**
```sh
moviebox download-movie "Avatar" --stream
```

### Python API Example

**Simple download:**
```python
from moviebox_api import MovieAuto
import asyncio

async def main():
    auto = MovieAuto()
    movie_file, subtitle_file = await auto.run("Avatar")
    print(f"Movie: {movie_file.saved_to}")
    print(f"Subtitle: {subtitle_file.saved_to}")

asyncio.run(main())
```



## 📖 Usage

## 🖥️ Command Line Interface

### Available Commands

```sh
moviebox --help
```

**Commands:**
- `download-movie` - Search and download a movie
- `download-series` - Search and download TV series episodes
- `interactive` - Launch interactive menu interface
- `homepage-content` - Show trending content
- `popular-search` - Show popular searches
- `item-details` - Get details about a movie/series
- `mirror-hosts` - Discover available mirror hosts

### Interactive Menu Guide

The interactive menu offers a clean, numbered interface:

```text
┌┬┐┌─┐┬  ┬┬┌─┐┌┐ ┌─┐─┐ ┬ 
││││ │└┐┌┘│├┤ ├┴┐│ │┌┴┬┘ 
┴ ┴└─┘ └┘ ┴└─┘└─┘└─┘┴ └─ 

DOWNLOAD OPTIONS
[1] Download Movie
[2] Download TV Series

STREAMING OPTIONS
[3] Stream Movie
[4] Stream TV Series

DISCOVER & INFO
[5] Show Homepage Content
[6] Show Popular Searches
[7] Show Mirror Hosts

[0] Exit
```

<details>
<summary><b>Navigation Tips</b></summary>

- Type a number (0-7) and press Enter
- Follow on-screen prompts
- Press `Ctrl+C` to exit anytime
- Press Enter without typing to use defaults

</details>

<details>
<summary><b>Quality Options</b></summary>

- `Best` - Highest available quality (recommended)
- `1080p` - Full HD (1920×1080)
- `720p` - HD (1280×720)
- `480p` - Standard Definition
- `360p` - Low quality, smaller file size
- `Worst` - Lowest available quality

</details>

<details>
<summary><b>Subtitle Options</b></summary>

- `Yes` - Download with subtitles (default)
- `No` - Download without subtitles
- `Subtitles only` - Download only subtitle files

</details>

### Download Commands

<details>
<summary><b>Download Movie</b></summary>

**Basic usage:**
```sh
moviebox download-movie "Avatar"
```

**With options:**
```sh
# Specific quality
moviebox download-movie "Avatar" --quality 1080p

# With year filter
moviebox download-movie "Avatar" --year 2009

# Custom directory
moviebox download-movie "Avatar" --dir ~/Movies

# Without subtitles
moviebox download-movie "Avatar" --no-caption

# Auto-confirm (no prompts)
moviebox download-movie "Avatar" --yes
```

**Common options:**
- `-y, --year` - Filter by release year
- `-q, --quality` - Video quality (best, 1080p, 720p, 480p, 360p, worst)
- `-d, --dir` - Download directory
- `-x, --language` - Subtitle language (default: English)
- `--no-caption` - Skip subtitle download
- `-Y, --yes` - Auto-confirm without prompts

[View all options](#download-movie-full-options)

</details>

<details>
<summary><b>Download TV Series</b></summary>

**Basic usage:**
```sh
moviebox download-series "Game of Thrones" -s 1 -e 1
```

**Download multiple episodes:**
```sh
# Download 5 episodes starting from S01E01
moviebox download-series "Game of Thrones" -s 1 -e 1 -l 5

# Download entire season
moviebox download-series "Game of Thrones" -s 1 -e 1 -l 100
```

**With options:**
```sh
# Specific quality
moviebox download-series "Merlin" -s 1 -e 1 --quality 720p

# Auto-confirm
moviebox download-series "Merlin" -s 1 -e 1 --yes

# Custom directory
moviebox download-series "Merlin" -s 1 -e 1 --dir ~/Series
```

**Download entire tv-series**

```sh
moviebox download-series "Merlin" -s 1 -e 1 --auto-mode
# This will download episodes across all available seasons
```

**Required options:**
- `-s, --season` - Season number (required)
- `-e, --episode` - Starting episode number (required)

**Common options:**
- `-l, --limit` - Number of episodes to download (default: 1)
- `-q, --quality` - Video quality
- `-x, --language` - Subtitle language
- `--no-caption` - Skip subtitles
- `-Y, --yes` - Auto-confirm

[View all options](#download-series-full-options)

</details>

---

<details id="download-movie-full-options">
<summary><b>Download Movie - All Options</b></summary>

```text
# python -m moviebox_api download-movie --help

Usage: python -m moviebox_api download-movie [OPTIONS] TITLE

  Search and download or stream movie.

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
                                  [default: {title} ({release_year}).{ext}]
  -C, --caption-filename-tmpl TEXT
                                  Template for generating caption filename
                                  [default: {title}
                                  ({release_year}).{lan}.{ext}]
  -t, --tasks INTEGER RANGE       Number of tasks to carry out the download
                                  [default: 5; 1<=x<=1000]
  -P, --part-dir DIRECTORY        Directory for temporarily saving the
                                  downloaded file-parts to  [default:
                                  /home/smartwa/git/smartwa/moviebox-api]
  -E, --part-extension TEXT       Filename extension for download parts
                                  [default: .part]
  -N, --chunk-size INTEGER        Streaming download chunk size in kilobytes
                                  [default: 256]
  -R, --timeout-retry-attempts INTEGER
                                  Number of times to retry download upon read
                                  request timing out  [default: 10]
  -B, --merge-buffer-size INTEGER RANGE
                                  Buffer size for merging the separated files
                                  in kilobytes [default : CHUNK_SIZE]
                                  [1<=x<=102400]
  -X, --stream-via [mpv|vlc]      Stream directly using the chosen media
                                  player instead of downloading
  -c, --colour TEXT               Progress bar display colour  [default: cyan]
  -U, --ascii                     Use unicode (smooth blocks) to fill the
                                  progress-bar meter
  -z, --disable-progress-bar      Do not show download progress-bar
  -I, --ignore-missing-caption    Proceed to download movie file even when
                                  caption file is missing
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

<details id="download-series-full-options">
<summary><b>Download Series - All Options</b></summary>

```text
# python -m moviebox_api download-series --help

Usage: python -m moviebox_api download-series [OPTIONS] TITLE

  Search and download or stream tv series.

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
                                  filename  [default: {title}
                                  S{season}E{episode}.{ext}]
  -C, --caption-filename-tmpl TEXT
                                  Template for generating caption filename
                                  [default: {title}
                                  S{season}E{episode}.{lan}.{ext}]
  -t, --tasks INTEGER RANGE       Number of tasks to carry out the download
                                  [default: 5; 1<=x<=1000]
  -P, --part-dir DIRECTORY        Directory for temporarily saving the
                                  downloaded file-parts to  [default:
                                  /home/smartwa/git/smartwa/moviebox-api]
  -f, --format [standard|group|struct]
                                  Ways of formating filename and saving the
                                  episodes.  group -> Organize episodes into
                                  separate folders based on seasons e.g
                                  Merlin/S1/Merlin S1E2.mp4 struct -> Save
                                  episodes in a hierarchical directory
                                  structure e.g Merlin (2009)/S1/E1.mp4
  -E, --part-extension TEXT       Filename extension for download parts
                                  [default: .part]
  -N, --chunk-size INTEGER        Streaming download chunk size in kilobytes
                                  [default: 256]
  -R, --timeout-retry-attempts INTEGER
                                  Number of times to retry download upon read
                                  request timing out  [default: 10]
  -B, --merge-buffer-size INTEGER RANGE
                                  Buffer size for merging the separated files
                                  in kilobytes [default : CHUNK_SIZE]
                                  [1<=x<=102400]
  -X, --stream-via [mpv|vlc]      Stream directly using the chosen media
                                  player instead of downloading
  -c, --colour TEXT               Progress bar display color  [default: cyan]
  -U, --ascii                     Use unicode (smooth blocks) to fill the
                                  progress-bar meter
  -z, --disable-progress-bar      Do not show download progress-bar
  -I, --ignore-missing-caption    Proceed to download episode file even when
                                  caption file is missing
  --leave / --no-leave            Keep all leaves of the progressbar
                                  [default: no-leave]
  --caption / --no-caption        Download caption file  [default: caption]
  -O, --caption-only              Download caption file only and ignore movie
  -A, --auto-mode                 When limit is 1 (default), download entire
                                  remaining seasons.
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

---

### Streaming via Media Players

Stream content directly without downloading (requires MPV or VLC player):

<details>
<summary><b>Stream Movies</b></summary>

```sh
# Stream a movie
moviebox download-movie "Avatar" --stream-via vlc

# Stream with subtitles
moviebox download-movie "Avatar" --stream-via mpv --caption

# Stream with specific language subtitles
moviebox download-movie "Avatar" --stream-via vlc --caption --language French

# Stream specific quality
moviebox download-movie "Avatar" --stream-via mpv --quality 720p
```

</details>

<details>
<summary><b>Stream TV Series</b></summary>

```sh
# Stream an episode
moviebox download-series "Game of Thrones" -s 1 -e 1 --stream-via vlc

# Stream with subtitles
moviebox download-series "Game of Thrones" -s 1 -e 1 --stream-via vlc --caption

# Stream specific quality
moviebox download-series "Breaking Bad" -s 1 -e 1 --stream-via vlc --quality 1080p
```

</details>

**Streaming Features:**
- ✅ No download required - watch immediately
- ✅ Automatic subtitle integration
- ✅ Proper HTTP header handling
- ✅ Auto-cleanup of temporary files
- ⚠️ Requires `moviebox-api[cli]` installation
- ⚠️ Requires MPV/VLC media player installed



## 🐍 Python API

### Simple Auto-Download

The easiest way to download content:

```python
from moviebox_api import MovieAuto
import asyncio

async def main():
    auto = MovieAuto()
    
    # Download movie with subtitle
    movie_file, subtitle_file = await auto.run("Avatar")
    print(f"Movie saved to: {movie_file.saved_to}")
    print(f"Subtitle saved to: {subtitle_file.saved_to}")

asyncio.run(main())
```

### Download with Progress Tracking

Monitor download progress in real-time:

```python
from moviebox_api import DownloadTracker, MovieAuto
import asyncio

async def progress_callback(progress: DownloadTracker):
    percent = (progress.downloaded_size / progress.expected_size) * 100
    print(f"[{percent:.2f}%] Downloading {progress.saved_to.name}", end="\r")

async def main():
    auto = MovieAuto()
    await auto.run("Avatar", progress_hook=progress_callback)

asyncio.run(main())
```

### Advanced Control with Downloader

For more control over the download process:

<details>
<summary><b>Download Movie with Confirmation</b></summary>

```python
from moviebox_api.cli import Downloader
import asyncio

async def main():
    downloader = Downloader()
    
    # User will be prompted to confirm the movie
    movie_file, subtitle_files = await downloader.download_movie("Avatar")
    
    print(f"Downloaded: {movie_file}")
    print(f"Subtitles: {subtitle_files}")

asyncio.run(main())
```

</details>

<details>
<summary><b>Download TV Series Episodes</b></summary>

```python
from moviebox_api.cli import Downloader
import asyncio

async def main():
    downloader = Downloader()
    
    # Download first 2 episodes of season 1
    episodes_map = await downloader.download_tv_series(
        "Merlin",
        season=1,
        episode=1,
        limit=2
        # limit = 1 
        # auto_mode = True # Download entire remaining seasons when limit=1
    )
    
    print(f"Downloaded episodes: {episodes_map}")

asyncio.run(main())
```

</details>

### Custom Configuration

```python
from moviebox_api import MovieAuto
import asyncio

async def main():
    # Customize download behavior
    auto = MovieAuto(
        caption_language="Spanish",  # Change subtitle language
        quality="720p",              # Set default quality
        download_dir="~/Downloads"   # Custom download directory
    )
    
    movie_file, subtitle_file = await auto.run("Avatar")

asyncio.run(main())
```

## 📚 Documentation

For comprehensive documentation with more examples:

- **[Full API Documentation](./docs/README.md)**
- **[Example Scripts](./docs/examples/)**
  - [Download Movie CLI](./docs/examples/download-movie-cli.py)
  - [Download Series CLI](./docs/examples/download-series-cli.py)
  - [Extractor Benchmark](./docs/examples/extractors-benchmark.py)


## ⚙️ Advanced Configuration

### Using Mirror Hosts

Moviebox.ph has [multiple mirror hosts](https://github.com/Simatwa/moviebox-api/issues/27). To use a specific mirror:

```sh
# Linux/macOS
export MOVIEBOX_API_HOST="h5.aoneroom.com"

# Windows (CMD)
set MOVIEBOX_API_HOST=h5.aoneroom.com

# Windows (PowerShell)
$env:MOVIEBOX_API_HOST="h5.aoneroom.com"
```

Or discover available mirrors:

```sh
moviebox mirror-hosts
```

### Command Shortcuts

```sh
# Instead of:
python -m moviebox_api download-movie "Avatar"

# Use:
moviebox download-movie "Avatar"
```

## Usage Tips

### Grouping Episodes

Organize episodes into separate folders based on seasons:

```sh
$ moviebox download-series Merlin -s 1 -e 1 --auto-mode --format group
```

```
./
  Merlin (2009)/
    S1/
      Merlin S1E1.mp4
      Merlin S1E2.mp4
    S2/
      Merlin S2E1.mp4
      Merlin S2E2.mp4
```

This structure keeps related episodes together within their season folders.

### Directory Structure

Save episodes in a hierarchical directory structure:

```sh
$ moviebox download-series Merlin -s 1 -e 1 --auto-mode --format struct
```

```
./
  Merlin (2009)/
    S1/
      E1.mp4
      E2.mp4
    S2/
      E1.mp4
      E2.mp4
```

This layout mirrors the TV series' episode order, making it easy to navigate and find specific episodes.


## ⚠️ Disclaimer

> "All videos and pictures on MovieBox are from the Internet, and their copyrights belong to the original creators. We only provide webpage services and do not store, record, or upload any content."  
> — *moviebox.ph (Sunday, July 13th, 2025)*

This is an unofficial API wrapper. Use responsibly and respect copyright laws in your jurisdiction.


## 👥 Contributors

We appreciate all contributions to this project! Thank you to everyone who has helped improve moviebox-api.

<div align="center">

<a href="https://github.com/Simatwa/moviebox-api/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Simatwa/moviebox-api" />
</a>

</div>

### How to Contribute

Contributions are welcome! Here's how you can help:

1. 🐛 **Report Bugs** - Open an issue describing the bug
2. 💡 **Suggest Features** - Share your ideas for improvements
3. 🔧 **Submit Pull Requests** - Fix bugs or add new features
4. 📖 **Improve Documentation** - Help make the docs better
5. ⭐ **Star the Project** - Show your support!

Please read our contribution guidelines before submitting a PR.

---

<div align="center">

**Made with ❤️**

[Report Bug](https://github.com/Simatwa/moviebox-api/issues) • [Request Feature](https://github.com/Simatwa/moviebox-api/issues) • [⭐ Star on GitHub](https://github.com/Simatwa/moviebox-api)

</div>
