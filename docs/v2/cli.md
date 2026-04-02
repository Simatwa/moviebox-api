There are several ways of accessing commandline **version 2**:

```sh
moviebox-v2--help
moviebox v2--help
python -m moviebox_api v2--help
python -m moviebox_api.v2--help
```

For this tutorial we shall be sticking to `moviebox-v1`
Search, download, and stream movies, TV series, anime, music, and educational content with subtitle support.

!!! info "Environment Variable Prefix"
    All environment variable overrides use the prefix `MOVIEBOX_`. For example, the v2 API host can be set via `MOVIEBOX_API_HOST_V2`.

---

## Global Options

```bash
moviebox-v2 [OPTIONS] COMMAND [ARGS]...
```

| Option | Description |
|--------|-------------|
| `--version` | Show the version and exit |
| `--help` | Show this message and exit |

---

## Commands

| Command | Description |
|---------|-------------|
| [`download-movie`](#download-movie) | Search, download or stream movies, anime, music, and educational content |
| [`download-series`](#download-series) | Search and download or stream TV series |
| [`homepage-content`](#homepage-content) | Show contents displayed at the landing page |
| [`item-details`](#item-details) | Show details of a particular movie/TV series |
| [`mirror-hosts`](#mirror-hosts) | Discover Moviebox mirror hosts |

---

## download-movie

Search, download or stream items under movie, anime, music, and education subject types.

```bash
moviebox-v2 download-movie [OPTIONS] TITLE
```

!!! note "v2 vs v1"
    Unlike `moviebox-v1`, this command supports multiple subject types via `-s / --subject-type`, allowing you to target anime, music, and education content in addition to movies.

### Arguments

| Argument | Description |
|----------|-------------|
| `TITLE` | Title of the item to search for *(required)* |

### Options

#### Search & Selection

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-s, --subject-type` | `movies\|education\|music\|anime` | `movies` | Subject type filter |
| `-y, --year` | `INTEGER` | `0` | Year filter for the item |
| `-q, --quality` | `worst\|best\|360p\|480p\|720p\|1080p` | `best` | Media quality to download |
| `-Y, --yes` | flag | — | Skip confirmation prompt |

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
| `-O, --caption-only` | flag | — | Download caption file only; skip video |
| `-I, --ignore-missing-caption` | flag | — | Proceed with download even if caption is missing |

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
| `-S, --simple` | flag | — | Show percentage and bar only |
| `--leave / --no-leave` | flag | `no-leave` | Keep all progress bar leaves after completion |

#### Logging

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-V, --verbose` | flag | — | Show detailed interactive output |
| `-Q, --quiet` | flag | — | Suppress all interactive output/logs |

### Examples

```bash
# Download a movie (best quality, auto-detect resume)
moviebox-v2 download-movie "Inception"

# Download an anime at 720p, skip confirmation
moviebox-v2 download-movie "Demon Slayer" -s anime -q 720p -Y

# Download educational content, save to specific directory
moviebox-v2 download-movie "Cosmos" -s education -d ~/Videos/Docs

# Stream music content directly with mpv
moviebox-v2 download-movie "Kendrick Lamar Concert" -s music -X mpv

# Download caption file only
moviebox-v2 download-movie "Inception" -O

# Test download without fetching
moviebox-v2 download-movie "Inception" -T
```

---

## download-series

Search and download or stream a TV series.

```bash
moviebox-v2 download-series [OPTIONS] TITLE
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

#### Episode Organization Details

!!! info "Format Modes"
    | Mode | Description | Example path |
    |------|-------------|--------------|
    | `standard` | All episodes saved flat in the output directory | `Merlin S1E2.mp4` |
    | `group` | Episodes organised into per-season subdirectories | `Merlin/S1/Merlin S1E2.mp4` |
    | `struct` | Hierarchical structure using episode numbers as filenames | `Merlin (2009)/S1/E1.mp4` |

**Group format** — episodes organized into season subfolders:

```bash
moviebox-v2 download-series Merlin -s 1 -e 1 --auto-mode --format group
```

```
Merlin/
  S1/
    Merlin S1E1.mp4
    Merlin S1E2.mp4
  S2/
    Merlin S2E1.mp4
```

**Struct format** — hierarchical directory structure using episode numbers as filenames:

```bash
moviebox-v2 download-series Merlin -s 1 -e 1 --auto-mode --format struct
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
moviebox-v2 download-series "Merlin" -s 1 -e 1

# Download episodes 3–7 of Season 2 at 720p, grouped into folders
moviebox-v2 download-series "Merlin" -s 2 -e 3 -l 5 -q 720p -f group

# Download all remaining episodes in season 1 starting from E1
moviebox-v2 download-series "The Last Kingdom" -s 1 -e 1 -A

# Stream S1E1 directly with VLC
moviebox-v2 download-series "Into the Badlands" -s 1 -e 1 -X vlc

# Download captions only for S3E1
moviebox-v2 download-series "Merlin" -s 3 -e 1 -O

# Download full season 1 with hierarchical folder structure, skip confirmation
moviebox-v2 download-series "Merlin" -s 1 -e 1 -A -f struct -Y -d ~/Series
```

---

## homepage-content

Show contents displayed at the Moviebox landing page.

```bash
moviebox-v2 homepage-content [OPTIONS]
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
moviebox-v2 homepage-content

# Filter by title keyword
moviebox-v2 homepage-content -T "action"

# Output as JSON
moviebox-v2 homepage-content -J

# Show banner items only
moviebox-v2 homepage-content -B
```

---

## item-details

Show details for a specific movie or TV series.

```bash
moviebox-v2 item-details [OPTIONS] TITLE
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
moviebox-v2 item-details "Inception"

# Look up a TV series with year filter
moviebox-v2 item-details "Merlin" -y 2008 -s tv_series

# Output full details as JSON
moviebox-v2 item-details "Inception" -J -F

# Skip confirmation prompt
moviebox-v2 item-details "The Batman" -y 2022 -Y
```

---

## mirror-hosts

Discover available Moviebox v2 mirror hosts.

```bash
moviebox-v2 mirror-hosts [OPTIONS]
```

!!! tip "Environment Variable"
    The v2 API host can also be set via the `MOVIEBOX_API_HOST_V2` environment variable.

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-J, --json` | flag | — | Output discovered hosts in JSON format |
| `-V, --verbose` | flag | — | Show detailed interactive output |
| `-Q, --quiet` | flag | — | Suppress all interactive output/logs |

### Examples

```bash
# List available mirror hosts
moviebox-v2 mirror-hosts

# Output as JSON
moviebox-v2 mirror-hosts -J

# Set host via environment variable
MOVIEBOX_API_HOST_V2=https://mirror.example.com moviebox-v2 mirror-hosts
```

---

## Filename Templates

Both `download-movie` and `download-series` support customisable filename templates using placeholder variables.

### Movie Templates (`-M`, `-C`)

| Variable | Description |
|----------|-------------|
| `{title}` | Item title |
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

## v1 vs v2 Differences

| Feature | moviebox-v1 | moviebox-v2 |
|---------|-------------|-------------|
| Subject types (`download-movie`) | movies only | `movies`, `anime`, `music`, `education` |
| `popular-search` command | ✓ | ✗ |
| API host env var | `MOVIEBOX_API_HOST` | `MOVIEBOX_API_HOST_V2` |
| `download-series` options | identical | identical |
| `homepage-content` options | identical | identical |
| `item-details` options | identical | identical |

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