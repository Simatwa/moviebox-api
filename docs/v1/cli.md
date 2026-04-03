There are several ways of accessing commandline **version 1**:

```sh
moviebox-v1 --help
moviebox v1 --help
python -m moviebox_api v1 --help
python -m moviebox_api.v1 --help
```

For this tutorial we shall be sticking to `moviebox-v1`

!!! info "Environment Variable Prefix"
    All environment variable overrides use the prefix `MOVIEBOX_`. For example, the API host can be set via `MOVIEBOX_API_HOST`.

---

## Global Options

```bash
moviebox-v1 [OPTIONS] COMMAND [ARGS]...
```

| Option | Description |
|--------|-------------|
| `--version` | Show the version and exit |
| `--help` | Show this message and exit |

---

## Commands

| Command | Description |
|---------|-------------|
| [`download-movie`](#download-movie) | Search and download or stream a movie |
| [`download-series`](#download-series) | Search and download or stream a TV series |
| [`homepage-content`](#homepage-content) | Show contents displayed at the landing page |
| [`item-details`](#item-details) | Show details of a particular movie/TV series |
| [`mirror-hosts`](#mirror-hosts) | Discover Moviebox mirror hosts |
| [`popular-search`](#popular-search) | Show movies/TV series many people are searching now |

---

## download-movie

Search and download or stream a movie.

```bash
moviebox-v1 download-movie [OPTIONS] TITLE
```

### Arguments

| Argument | Description |
|----------|-------------|
| `TITLE` | Title of the movie to search for *(required)* |

### Options

#### Search & Selection

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-y, --year` | `INTEGER` | `0` | Year filter for the movie |
| `-q, --quality` | `worst\|best\|360p\|480p\|720p\|1080p` | `best` | Media quality to download |
| `-Y, --yes` | flag | — | Skip movie confirmation prompt |

#### Output Paths

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-d, --dir` | `DIRECTORY` | `$PWD` | Directory to save the movie file |
| `-D, --caption-dir` | `DIRECTORY` | `$PWD` | Directory to save the caption file |
| `-P, --part-dir` | `DIRECTORY` | `$PWD` | Directory for temporary download part files |

#### File Naming

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-M, --movie-filename-tmpl` | `TEXT` | `{title} ({release_year}).{ext}` | Template for the movie filename |
| `-C, --caption-filename-tmpl` | `TEXT` | `{title} ({release_year}).{lan}.{ext}` | Template for the caption filename |
| `-E, --part-extension` | `TEXT` | `.part` | File extension for download part files |

#### Caption Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-x, --language` | `TEXT` | `English` | Caption language filter |
| `--caption / --no-caption` | flag | `caption` | Enable or disable caption download |
| `-O, --caption-only` | flag | — | Download caption file only; skip movie |
| `-I, --ignore-missing-caption` | flag | — | Proceed with movie download even if caption is missing |

#### Download Behaviour

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-m, --mode` | `start\|resume\|auto` | `auto` | Download mode: start fresh, resume, or detect automatically |
| `-t, --tasks` | `INTEGER (1–1000)` | `5` | Number of concurrent download tasks |
| `-N, --chunk-size` | `INTEGER` | `256` | Streaming chunk size in kilobytes |
| `-R, --timeout-retry-attempts` | `INTEGER` | `10` | Retry attempts on read timeout |
| `-B, --merge-buffer-size` | `INTEGER (1–102400)` | `CHUNK_SIZE` | Buffer size (KB) for merging part files |
| `-T, --test` | flag | — | Test download viability without actually downloading |

#### Streaming

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-X, --stream-via` | `mpv\|vlc` | — | Stream directly via the chosen media player instead of downloading |

#### Progress Bar

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-c, --colour` | `TEXT` | `cyan` | Progress bar colour |
| `-U, --ascii` | flag | — | Use Unicode smooth blocks for the progress bar meter |
| `-z, --disable-progress-bar` | flag | — | Suppress the download progress bar |
| `-S, --simple` | flag | — | Show percentage and bar only (no extra info) |
| `--leave / --no-leave` | flag | `no-leave` | Keep all progress bar leaves after completion |

#### Logging

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-V, --verbose` | flag | — | Show detailed interactive output |
| `-Q, --quiet` | flag | — | Suppress all interactive output/logs |

### Examples

```bash
# Download best quality, auto-detect resume
moviebox-v1 download-movie "Inception"

# Download 720p, skip confirmation, save to ~/Movies
moviebox-v1 download-movie "Inception" -q 720p -Y -d ~/Movies

# Download 1080p from a specific year, ignore missing subtitles
moviebox-v1 download-movie "The Batman" -y 2022 -q 1080p -I

# Stream directly with mpv
moviebox-v1 download-movie "Inception" -X mpv

# Download caption file only
moviebox-v1 download-movie "Inception" -O

# Test download without fetching
moviebox-v1 download-movie "Inception" -T
```

---

## download-series

Search and download or stream a TV series.

```bash
moviebox-v1 download-series [OPTIONS] TITLE
```

### Arguments

| Argument | Description |
|----------|-------------|
| `TITLE` | Title of the TV series to search for *(required)* |

### Options

#### Search & Selection

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-y, --year` | `INTEGER` | `0` | Year filter for the series |
| `-s, --season` | `INTEGER (1–1000)` | — | Season number *(required)* |
| `-e, --episode` | `INTEGER (1–1000)` | — | Episode offset within the season *(required)* |
| `-l, --limit` | `INTEGER (1–1000)` | `1` | Total number of episodes to download |
| `-q, --quality` | `worst\|best\|360p\|480p\|720p\|1080p` | `best` | Media quality to download |
| `-Y, --yes` | flag | — | Skip series confirmation prompt |
| `-A, --auto-mode` | flag | — | When limit is 1 (default), download all remaining episodes in the season |

#### Output Paths

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-d, --dir` | `DIRECTORY` | `$PWD` | Directory to save the series files |
| `-D, --caption-dir` | `DIRECTORY` | `$PWD` | Directory to save caption files |
| `-P, --part-dir` | `DIRECTORY` | `$PWD` | Directory for temporary download part files |

#### File Naming & Structure

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-L, --episode-filename-tmpl` | `TEXT` | `{title} S{season}E{episode}.{ext}` | Template for episode filenames |
| `-C, --caption-filename-tmpl` | `TEXT` | `{title} S{season}E{episode}.{lan}.{ext}` | Template for caption filenames |
| `-E, --part-extension` | `TEXT` | `.part` | File extension for download part files |
| `-f, --format` | `standard\|group\|struct` | — | Episode file organisation format (see below) |

!!! info "Format Modes"
    | Mode | Description | Example |
    |------|-------------|---------|
    | `standard` | Save all episodes flat in the output directory | `Merlin S1E2.mp4` |
    | `group` | Organise episodes into per-season subdirectories | `Merlin/S1/Merlin S1E2.mp4` |
    | `struct` | Hierarchical directory structure | `Merlin (2009)/S1/E1.mp4` |


#### Episode Organization Details

**Group format** — episodes organized into season subfolders:

```sh
moviebox-v1 download-series Merlin -s 1 -e 1 --auto-mode --format group
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
moviebox-v1 download-series Merlin -s 1 -e 1 --auto-mode --format struct
```

```
Merlin (2009)/
  S1/
    E1.mp4
    E2.mp4
  S2/
    E1.mp4
```

#### Caption Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-x, --language` | `TEXT` | `English` | Caption language filter |
| `--caption / --no-caption` | flag | `caption` | Enable or disable caption download |
| `-O, --caption-only` | flag | — | Download caption files only; skip video |
| `-I, --ignore-missing-caption` | flag | — | Proceed with episode download even if caption is missing |

#### Download Behaviour

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-m, --mode` | `start\|resume\|auto` | `auto` | Download mode: start fresh, resume, or detect automatically |
| `-t, --tasks` | `INTEGER (1–1000)` | `5` | Number of concurrent download tasks |
| `-N, --chunk-size` | `INTEGER` | `256` | Streaming chunk size in kilobytes |
| `-R, --timeout-retry-attempts` | `INTEGER` | `10` | Retry attempts on read timeout |
| `-B, --merge-buffer-size` | `INTEGER (1–102400)` | `CHUNK_SIZE` | Buffer size (KB) for merging part files |
| `-T, --test` | flag | — | Test download viability without actually downloading |

#### Streaming

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-X, --stream-via` | `mpv\|vlc` | — | Stream directly via the chosen media player |

#### Progress Bar

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-c, --colour` | `TEXT` | `cyan` | Progress bar colour |
| `-U, --ascii` | flag | — | Use Unicode smooth blocks for the progress bar meter |
| `-z, --disable-progress-bar` | flag | — | Suppress the download progress bar |
| `-S, --simple` | flag | — | Show percentage and bar only |
| `--leave / --no-leave` | flag | `no-leave` | Keep all progress bar leaves after completion |

#### Logging

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-V, --verbose` | flag | — | Show detailed interactive output |
| `-Q, --quiet` | flag | — | Suppress all interactive output/logs |

### Examples

```bash
# Download S1E1 of Merlin
moviebox-v1 download-series "Merlin" -s 1 -e 1

# Download episodes 3–7 of Season 2, 720p, organised into folders
moviebox-v1 download-series "Merlin" -s 2 -e 3 -l 5 -q 720p -f group

# Download all remaining episodes in season 1 starting from E1
moviebox-v1 download-series "The Last Kingdom" -s 1 -e 1 -A

# Stream S1E1 directly with VLC
moviebox-v1 download-series "Into the Badlands" -s 1 -e 1 -X vlc

# Download captions only for S3E1
moviebox-v1 download-series "Merlin" -s 3 -e 1 -O

# Download with hierarchical folder structure, skip confirmation
moviebox-v1 download-series "Merlin" -s 1 -e 1 -l 13 -f struct -Y -d ~/Series
```

---

## homepage-content

Show contents displayed at the Moviebox landing page.

```bash
moviebox-v1 homepage-content [OPTIONS]
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-J, --json` | flag | `False` | Output details in JSON format |
| `-T, --title` | `TEXT` | `None` | Filter contents by title |
| `-B, --banner` | flag | `False` | Show banner content only |
| `-V, --verbose` | flag | — | Show detailed interactive output |
| `-Q, --quiet` | flag | — | Suppress all interactive output/logs |

### Examples

```bash
# List all homepage content
moviebox-v1 homepage-content

# Filter by title keyword
moviebox-v1 homepage-content -T "action"

# Output as JSON
moviebox-v1 homepage-content -J

# Show banner items only
moviebox-v1 homepage-content -B
```

---

## item-details

Show details for a specific movie or TV series.

```bash
moviebox-v1 item-details [OPTIONS] TITLE
```

### Arguments

| Argument | Description |
|----------|-------------|
| `TITLE` | Title to look up *(required)* |

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-y, --year` | `INTEGER` | `0` | Year filter for the item |
| `-s, --subject-type` | `all\|movies\|tv_series\|education\|music\|anime` | `all` | Subject type filter |
| `-Y, --yes` | flag | — | Skip item confirmation prompt |
| `-J, --json` | flag | — | Output details in JSON format instead of tabulated |
| `-F, --full` | flag | — | Show all available details |
| `-V, --verbose` | flag | — | Show detailed interactive output |
| `-Q, --quiet` | flag | — | Suppress all interactive output/logs |

### Examples

```bash
# Look up a movie
moviebox-v1 item-details "Inception"

# Look up a TV series with year filter
moviebox-v1 item-details "Merlin" -y 2008 -s tv_series

# Output full details as JSON
moviebox-v1 item-details "Inception" -J -F

# Skip confirmation prompt
moviebox-v1 item-details "The Batman" -y 2022 -Y
```

---

## mirror-hosts

Discover available Moviebox mirror hosts.

```bash
moviebox-v1 mirror-hosts [OPTIONS]
```

!!! tip "Environment Variable"
    The API host can also be set via the `MOVIEBOX_API_HOST` environment variable.

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-J, --json` | flag | — | Output discovered hosts in JSON format |
| `-V, --verbose` | flag | — | Show detailed interactive output |
| `-Q, --quiet` | flag | — | Suppress all interactive output/logs |

### Examples

```bash
# List available mirror hosts
moviebox-v1 mirror-hosts

# Output as JSON
moviebox-v1 mirror-hosts -J

# Set host via environment variable
export MOVIEBOX_API_HOST="https://h5.aoneroom.com"
```

---

## popular-search

Show movies and TV series that many users are currently searching for.

```bash
moviebox-v1 popular-search [OPTIONS]
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-J, --json` | flag | `False` | Output results in JSON format |

### Examples

```bash
# Show popular searches (tabulated)
moviebox-v1 popular-search

# Output as JSON
moviebox-v1 popular-search -J
```

---

## Filename Templates

Both `download-movie` and `download-series` support customisable filename templates using placeholder variables.

### Movie Templates (`-M`, `-C`)

| Variable | Description |
|----------|-------------|
| `{title}` | Movie title |
| `{release_year}` | Release year |
| `{ext}` | File extension |
| `{lan}` | Caption language *(caption template only)* |

**Defaults:**

```
Movie:   {title} ({release_year}).{ext}
Caption: {title} ({release_year}).{lan}.{ext}
```

### Series Templates (`-L`, `-C`)

| Variable | Description |
|----------|-------------|
| `{title}` | Series title |
| `{season}` | Season number (zero-padded) |
| `{episode}` | Episode number (zero-padded) |
| `{ext}` | File extension |
| `{lan}` | Caption language *(caption template only)* |

**Defaults:**

```
Episode: {title} S{season}E{episode}.{ext}
Caption: {title} S{season}E{episode}.{lan}.{ext}
```

---

## Common Flags Reference

These flags are shared across multiple commands:

| Flag | Commands | Description |
|------|----------|-------------|
| `-V, --verbose` | all | Show detailed interactive output |
| `-Q, --quiet` | all | Suppress all interactive output/logs |
| `-J, --json` | most | Output in JSON format |
| `-Y, --yes` | download, item-details | Skip confirmation prompts |
| `-T, --test` | download commands | Test without downloading |
| `-X, --stream-via` | download commands | Stream via `mpv` or `vlc` |
| `-O, --caption-only` | download commands | Fetch captions only |
| `-I, --ignore-missing-caption` | download commands | Proceed even if caption is absent |