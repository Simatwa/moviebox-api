# moviebox-v3 CLI Reference

Search, download, and stream movies, TV series, anime, music, and educational content.

!!! info "Environment Variable Prefix"
    All environment variable overrides use the prefix `MOVIEBOX_V3`.

---

## Global Options

```bash
moviebox-v3 [OPTIONS] COMMAND [ARGS]...
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

---

## download-movie

Search and download or stream a movie.

```bash
moviebox-v3 download-movie [OPTIONS] TITLE
```

### Arguments

| Argument | Description |
|----------|-------------|
| `TITLE` | Title of the item to search for *(required)* |

### Options

#### Search & Selection

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-s, --subject-type` | `movies\|education\|music\|anime\|unknown` | `movies` | Subject type filter |
| `-y, --year` | `INTEGER` | `0` | Year filter for the movie |
| `-q, --quality` | `360p\|480p\|720p\|1080p\|best\|worst` | `best` | Media quality to download |
| `-u, --dub` | `TEXT` | `Original Audio` | Dub language name or code |
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
| `-x, --language` | `TEXT` | `English` | Caption language filter. Pass multiple times to download multiple languages |
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
# Download a movie (best quality, auto-detect resume), skip confirmation, test only
moviebox-v3 download-movie avatar -YT

# Download with multiple caption languages (English + Filipino)
moviebox-v3 download-movie avatar -YT -x en -x filipino

# Download Hindi dub
moviebox-v3 download-movie avatar --dub hi -YT

# Download music content
moviebox-v3 download-movie walker -s music -YT

# Download anime at 1080p, save to directory
moviebox-v3 download-movie "Demon Slayer" -s anime -q 1080p -Y -d ~/Videos/Anime

# Stream directly with mpv
moviebox-v3 download-movie "Avengers Endgame" -X mpv
```

---

## download-series

Search and download or stream a TV series.

```bash
moviebox-v3 download-series [OPTIONS] TITLE
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
| `-s, --season` | `INTEGER (1–1000)` | `1` | Season number to start processing from |
| `-e, --episode` | `INTEGER (1–1000)` | `1` | Episode within the selected season to start from |
| `-l, --limit` | `INTEGER (-1–1000)` | `1` | Total episodes to download; set `-1` to disable the limit |
| `-q, --quality` | `360p\|480p\|720p\|1080p\|best\|worst` | `best` | Media quality to download |
| `-u, --dub` | `TEXT` | `Original Audio` | Dub language name or code |
| `-Y, --yes` | flag | — | Skip series confirmation prompt |
| `-A, --auto-mode` | flag | — | Download all remaining episodes across all remaining seasons (shortcut for `--limit -1`) |

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
| `-f, --format` | `standard\|group\|struct` | `standard` | Episode file organisation format (see below) |

#### Episode Organization Details

!!! info "Format Modes"
    | Mode | Description | Example path |
    |------|-------------|--------------|
    | `standard` | All episodes saved flat in the output directory | `Merlin S1E2.mp4` |
    | `group` | Episodes organised into per-season subdirectories | `Merlin/S1/Merlin S1E2.mp4` |
    | `struct` | Hierarchical structure using episode numbers as filenames | `Merlin (2009)/S1/E1.mp4` |

**Group format** — episodes organized into season subfolders:

```bash
moviebox-v3 download-series Merlin -s 1 -e 1 --auto-mode --format group
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
moviebox-v3 download-series Merlin -s 1 -e 1 --auto-mode --format struct
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
| `-x, --language` | `TEXT` | `English` | Caption language filter. Pass multiple times to download multiple languages |
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
# Download S1E1, skip confirmation, test only
moviebox-v3 download-series 'A Knight of the Seven Kingdoms' -s 1 -e 1 -YT

# Download with a specific dub (Telugu)
moviebox-v3 download-series 'A Knight of the Seven Kingdoms' -s 1 -e 1 --dub 'Telugu dub' -YT

# Download with multiple caption languages (English + Filipino)
moviebox-v3 download-series banshee -YT -x en -x filipino

# Download with multiple caption languages and a specific dub
moviebox-v3 download-series banshee -YT -x en -x filipino --dub en

# Download all remaining episodes across all seasons from S1E1
moviebox-v3 download-series "Merlin" -A

# Equivalent to --auto-mode using --limit -1
moviebox-v3 download-series "Merlin" -s 1 -e 1 -l -1

# Download episodes 3–7 of Season 2 at 720p, grouped into folders
moviebox-v3 download-series "Merlin" -s 2 -e 3 -l 5 -q 720p -f group

# Stream S1E1 directly with VLC
moviebox-v3 download-series "Into the Badlands" -s 1 -e 1 -X vlc

# Download full series with hierarchical folder structure, skip confirmation
moviebox-v3 download-series "Merlin" -A -f struct -Y -d ~/Series
```

---

## homepage-content

Show contents displayed at the Moviebox landing page.

```bash
moviebox-v3 homepage-content [OPTIONS]
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
moviebox-v3 homepage-content

# Filter by title keyword
moviebox-v3 homepage-content -T "action"

# Output as JSON
moviebox-v3 homepage-content -J

# Show banner items only
moviebox-v3 homepage-content -B
```

---

## item-details

Show details for a specific movie or TV series.

```bash
moviebox-v3 item-details [OPTIONS] TITLE
```

### Arguments

| Argument | Description |
|----------|-------------|
| `TITLE` | Title to look up *(required)* |

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-y, --year` | `INTEGER` | `0` | Year filter for the item |
| `-s, --subject-type` | `all\|movies\|tv_series\|education\|music\|anime\|unknown` | `all` | Subject type filter |
| `-Y, --yes` | flag | — | Skip item confirmation prompt |
| `-J, --json` | flag | — | Output details in JSON format instead of tabulated |
| `-V, --verbose` | flag | — | Show detailed interactive output |
| `-Q, --quiet` | flag | — | Suppress all interactive output/logs |

### Examples

```bash
# Look up a movie
moviebox-v3 item-details "Avengers Endgame"

# Look up a TV series with year filter
moviebox-v3 item-details "Merlin" -y 2008 -s tv_series

# Output as JSON, skip confirmation
moviebox-v3 item-details "Inception" -J -Y

# Filter by subject type
moviebox-v3 item-details "Demon Slayer" -s anime
```

---

## Filename Templates

Both `download-movie` and `download-series` support customisable filename templates using placeholder variables.

### Video File Placeholders (`-M`, `-L`)

| Placeholder | Description |
|-------------|-------------|
| `{title}` | Title of the movie or series |
| `{release_year}` | Release year |
| `{release_date}` | Full release date |
| `{resolution}` | Video resolution (e.g. `1080p`) |
| `{ext}` | File extension |
| `{size_string}` | Human-readable file size |
| `{season}` | Season number *(series only)* |
| `{episode}` | Episode number *(series only)* |
| `{episode_title}` | Episode title *(series only)* |
| `{duration}` | Media duration |
| `{codec_name}` | Video codec name |

### Caption File Placeholders (`-C`)

| Placeholder | Description |
|-------------|-------------|
| `{title}` | Title of the movie or series |
| `{release_year}` | Release year |
| `{release_date}` | Full release date |
| `{ext}` | File extension |
| `{size_string}` | Human-readable file size |
| `{id}` | Caption track identifier |
| `{lan}` | Caption language code (e.g. `en`) |
| `{lan_name}` | Caption language full name (e.g. `English`) |
| `{delay}` | Caption sync delay value |
| `{season}` | Season number *(series only)* |
| `{episode}` | Episode number *(series only)* |
| `{episode_title}` | Episode title *(series only)* |

### Defaults

```
Movie file:    {title} ({release_year}).{ext}
Movie caption: {title} ({release_year}).{lan}.{ext}

Episode file:    {title} S{season}E{episode}.{ext}
Episode caption: {title} S{season}E{episode}.{lan}.{ext}
```

---

## v1 / v2 / v3 Comparison

| Feature | v1 | v2 | v3 |
|---------|----|----|-----|
| Subtitle/caption support | ✓ | ✓ | ✓ |
| Dub language selection (`-u / --dub`) | ✗ | ✗ | ✓ |
| Subject types (`download-movie`) | movies only | movies, anime, music, education | movies, anime, music, education, **unknown** |
| Subject types (`item-details`) | all, movies, tv_series, education, music, anime | all, movies, tv_series, education, music, anime | all, movies, tv_series, education, music, anime, **unknown** |
| `popular-search` command | ✓ | ✗ | ✗ |
| `mirror-hosts` command | ✓ | ✓ | ✗ |
| `--season` / `--episode` defaults | required | required | `1` / `1` |
| `--limit -1` (disable limit) | ✗ | ✗ | ✓ |
| env var prefix | `MOVIEBOX` | `MOVIEBOX` | `MOVIEBOX_V3` |
| API host env var | `MOVIEBOX_API_HOST` | `MOVIEBOX_API_HOST_V2` | *(NOT REQUIRED)* |

---

## Common Flags Reference

| Flag | Commands | Description |
|------|----------|-------------|
| `-V, --verbose` | all | Show detailed interactive output |
| `-Q, --quiet` | all | Suppress all interactive output/logs |
| `-J, --json` | most | Output in JSON format |
| `-Y, --yes` | download, item-details | Skip confirmation prompts |
| `-T, --test` | download commands | Test without downloading |
| `-X, --stream-via` | download commands | Stream via `mpv` or `vlc` |
| `-u, --dub` | download commands | Select dub language |
| `-x, --language` | download commands | Caption language; repeatable for multiple languages |
| `-O, --caption-only` | download commands | Fetch captions only |
| `-I, --ignore-missing-caption` | download commands | Proceed even if caption is absent |