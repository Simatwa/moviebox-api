# moviebox-api

**Unofficial Python wrapper for moviebox.ph** — Search, discover, and download movies & TV series with subtitles.

[![PyPI version](https://badge.fury.io/py/moviebox-api.svg)](https://pypi.org/project/moviebox-api) [![Downloads](https://pepy.tech/badge/moviebox-api)](https://pepy.tech/project/moviebox-api)

---

## Features

- 🎬 Download movies and TV series in multiple resolutions
- 📝 Multi-language subtitle support
- 🎥 Stream directly with MPV player (no download needed)
- ⚡ Fast parallel downloads (5x faster than standard)
- 🎯 Interactive menu interface
- 🐍 Clean Python API with async/sync support

---

## Installation

**For CLI usage:**
```sh
pip install "moviebox-api[cli]"
```

**For Python development:**
```sh
pip install moviebox-api
```

**Optional - MPV Player (for streaming):**
- **Linux:** `sudo apt install mpv` or `sudo pacman -S mpv`
- **macOS:** `brew install mpv`
- **Windows:** Download from [mpv.io](https://mpv.io/installation/)

---

## Quick Start

### Interactive Menu (Recommended)

Launch the user-friendly interface:

```sh
moviebox interactive
```

Navigate with numbers 0-7 and follow on-screen prompts.

### Command Line

**Download a movie:**
```sh
moviebox download-movie "Avatar"
```

**Download a TV episode:**
```sh
moviebox download-series "Game of Thrones" -s 1 -e 1
```

**Stream without downloading:**
```sh
moviebox download-movie "Avatar" --stream
```

### Python API

```python
from moviebox_api import MovieAuto
import asyncio

async def main():
    auto = MovieAuto()
    movie_file, subtitle_file = await auto.run("Avatar")
    print(f"Downloaded to: {movie_file.saved_to}")

asyncio.run(main())
```

---

## Command Line Usage

### Download Movies

**Basic:**
```sh
moviebox download-movie "Avatar"
```

**Common options:**
```sh
moviebox download-movie "Avatar" \
  --quality 1080p \
  --year 2009 \
  --dir ~/Movies \
  --language Spanish \
  --yes  # Auto-confirm
```

**Available qualities:** `best`, `1080p`, `720p`, `480p`, `360p`, `worst`

### Download TV Series

**Basic:**
```sh
moviebox download-series "Game of Thrones" -s 1 -e 1
```

**Download multiple episodes:**
```sh
# Download 5 episodes starting from S01E01
moviebox download-series "Game of Thrones" -s 1 -e 1 -l 5
```

**Required flags:**
- `-s, --season` - Season number
- `-e, --episode` - Starting episode number

**Optional flags:**
- `-l, --limit` - Number of episodes to download (default: 1)
- `-q, --quality` - Video quality
- `-Y, --yes` - Skip confirmation prompts

### Streaming with MPV

Stream content directly without downloading:

```sh
# Stream a movie
moviebox download-movie "Avatar" --stream --caption

# Stream a TV episode
moviebox download-series "Breaking Bad" -s 1 -e 1 --stream
```

**Requirements:** MPV player must be installed.

---

## Python API

### Basic Download

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

### Download with Progress Tracking

```python
from moviebox_api import DownloadTracker, MovieAuto
import asyncio

async def progress_callback(progress: DownloadTracker):
    percent = (progress.downloaded_size / progress.expected_size) * 100
    print(f"[{percent:.2f}%] {progress.saved_to.name}", end="\r")

async def main():
    auto = MovieAuto()
    await auto.run("Avatar", progress_hook=progress_callback)

asyncio.run(main())
```

### Custom Configuration

```python
from moviebox_api import MovieAuto
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

### Download TV Series

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
    )
    
    print(f"Downloaded: {episodes_map}")

asyncio.run(main())
```

---

## Advanced Configuration

### Using Mirror Hosts

If the default host is unavailable, use an alternative mirror:

**Linux/macOS:**
```sh
export MOVIEBOX_API_HOST="h5.aoneroom.com"
```

**Windows (PowerShell):**
```powershell
$env:MOVIEBOX_API_HOST="h5.aoneroom.com"
```

**Discover available mirrors:**
```sh
moviebox mirror-hosts
```

---

## Additional Commands

**Show trending content:**
```sh
moviebox homepage-content
```

**Show popular searches:**
```sh
moviebox popular-search
```

**Get movie/series details:**
```sh
moviebox item-details
```

**View all commands:**
```sh
moviebox --help
```

---

## Termux Support (Android)

```sh
pip install moviebox-api --no-deps
pip install 'pydantic==2.9.2'
pip install rich click bs4 httpx throttlebuster
```

---

## Documentation

- **[Full API Documentation](./docs/README.md)**
- **[Example Scripts](./docs/examples/)**

---

## Contributing

Contributions are welcome! Here's how to help:

1. 🐛 **Report bugs** - Open an issue with details
2. 💡 **Suggest features** - Share your ideas
3. 🔧 **Submit PRs** - Fix bugs or add features
4. ⭐ **Star the project** - Show your support

---

## Disclaimer

All videos and content are sourced from moviebox.ph. This is an unofficial API wrapper. Copyrights belong to their respective owners. Use responsibly and respect copyright laws in your jurisdiction.

---

<div align="center">

**Made with ❤️**

[Report Bug](https://github.com/Simatwa/moviebox-api/issues) · [Request Feature](https://github.com/Simatwa/moviebox-api/issues) · [⭐ Star on GitHub](https://github.com/Simatwa/moviebox-api)

</div>