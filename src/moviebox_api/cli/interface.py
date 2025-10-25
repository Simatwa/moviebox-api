"""Contains the actual console commands"""

import logging
import os
import sys
from pathlib import Path

import click

from moviebox_api import __version__
from moviebox_api.cli.downloader import Downloader
from moviebox_api.cli.extras import (
    homepage_content_command,
    item_details_command,
    mirror_hosts_command,
    popular_search_command,
)
from moviebox_api.cli.helpers import (
    command_context_settings,
    media_player_name_func_map,
    prepare_start,
    process_download_runner_params,
    show_any_help,
)
from moviebox_api.cli.interactive import run_interactive_menu
from moviebox_api.constants import (
    CURRENT_WORKING_DIR,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_READ_TIMEOUT_ATTEMPTS,
    DEFAULT_TASKS,
    DEFAULT_TASKS_LIMIT,
    DOWNLOAD_PART_EXTENSION,
    DOWNLOAD_QUALITIES,
    DownloadMode,
)
from moviebox_api.download import (
    CaptionFileDownloader,
    MediaFileDownloader,
)
from moviebox_api.helpers import get_event_loop

__all__ = [
    "download_movie_command",
    "download_tv_series_command",
    "mirror_hosts_command",
    "homepage_content_command",
    "popular_search_command",
    "item_details_command",
    "interactive_menu_command",
]

DEBUG = os.getenv("DEBUG", "0") == "1"


@click.group()
@click.version_option(version=__version__)
def moviebox():
    """Search and download movies/tv-series and their subtitles. envvar-prefix : MOVIEBOX"""


@click.command(context_settings=command_context_settings)
@click.argument("title")
@click.option(
    "-y",
    "--year",
    type=click.INT,
    help="Year filter for the movie to proceed with",
    default=0,
    show_default=True,
)
@click.option(
    "-q",
    "--quality",
    help="Media quality to be downloaded",
    type=click.Choice(DOWNLOAD_QUALITIES, case_sensitive=False),
    default="BEST",
    show_default=True,
)
@click.option(
    "-d",
    "--dir",
    help="Directory for saving the movie to",
    type=click.Path(exists=True, file_okay=False),
    default=CURRENT_WORKING_DIR,
    show_default=True,
)
@click.option(
    "-D",
    "--caption-dir",
    help="Directory for saving the caption file to",
    type=click.Path(exists=True, file_okay=False),
    default=CURRENT_WORKING_DIR,
    show_default=True,
)
@click.option(
    "-m",
    "--mode",
    type=click.Choice(DownloadMode.map().keys(), case_sensitive=False),
    help="Start the download, resume or set automatically",
    default=DownloadMode.AUTO.value,
    show_default=True,
)
@click.option(
    "-x",
    "--language",
    help="Caption language filter",
    multiple=True,
    default=["English"],
    show_default=True,
)
@click.option(
    "-M",
    "--movie-filename-tmpl",
    help="Template for generating movie filename",
    default=MediaFileDownloader.movie_filename_template,
    show_default=True,
)
@click.option(
    "-C",
    "--caption-filename-tmpl",
    help="Template for generating caption filename",
    default=CaptionFileDownloader.movie_filename_template,
    show_default=True,
)
@click.option(
    "-t",
    "--tasks",
    type=click.IntRange(1, DEFAULT_TASKS_LIMIT),
    help="Number of tasks to carry out the download",
    default=DEFAULT_TASKS,
    show_default=True,
)
@click.option(
    "-P",
    "--part-dir",
    help="Directory for temporarily saving the downloaded file-parts to",
    type=click.Path(exists=True, file_okay=False, writable=True, resolve_path=True),
    default=CURRENT_WORKING_DIR,
    show_default=True,
)
@click.option(
    "-E",
    "--part-extension",
    help="Filename extension for download parts",
    default=DOWNLOAD_PART_EXTENSION,
    show_default=True,
)
@click.option(
    "-N",
    "--chunk-size",
    type=click.INT,
    help="Streaming download chunk size in kilobytes",
    default=DEFAULT_CHUNK_SIZE,
    show_default=True,
)
@click.option(
    "-R",
    "--timeout-retry-attempts",
    type=click.INT,
    help="Number of times to retry download upon read request timing out",
    show_default=True,
    default=DEFAULT_READ_TIMEOUT_ATTEMPTS,
)
@click.option(
    "-B",
    "--merge-buffer-size",
    type=click.IntRange(1, 102400),
    help="Buffer size for merging the separated files in kilobytes [default : CHUNK_SIZE]",
    show_default=True,
)
@click.option(
    "-X",
    "--stream-via",
    type=click.Choice(media_player_name_func_map.keys()),
    default=None,
    show_default=True,
    help="Stream directly using the chosen media player instead of downloading",
)
@click.option(
    "-c",
    "--colour",
    help="Progress bar display colour",
    default="cyan",
    show_default=True,
)
@click.option(
    "-U",
    "--ascii",
    is_flag=True,
    help="Use unicode (smooth blocks) to fill the progress-bar meter",
)
@click.option(
    "-z",
    "--disable-progress-bar",
    is_flag=True,
    help="Do not show download progress-bar",
)
@click.option(
    "-I",
    "--ignore-missing-caption",
    is_flag=True,
    help="Proceed to download movie file even when caption file is missing",
    show_default=True,
)
@click.option(
    "--leave/--no-leave",
    default=False,
    help="Keep all leaves of the progress-bar",
    show_default=True,
)
@click.option(
    "--caption/--no-caption",
    help="Download caption file",
    default=True,
    show_default=True,
)
@click.option(
    "-O",
    "--caption-only",
    is_flag=True,
    help="Download caption file only and ignore movie",
)
@click.option(
    "-S",
    "--simple",
    is_flag=True,
    help="Show download percentage and bar only in progressbar",
)
@click.option(
    "-T",
    "--test",
    is_flag=True,
    help="Just test if download is possible but do not actually download",
)
@click.option(
    "-V",
    "--verbose",
    count=True,
    help="Show more detailed interactive texts",
    default=0,
)
@click.option(
    "-Q",
    "--quiet",
    is_flag=True,
    help="Disable showing interactive texts on the progress (logs)",
)
@click.option(
    "-Y",
    "--yes",
    is_flag=True,
    help="Do not prompt for movie confirmation",
)
@click.help_option("-h", "--help")
def download_movie_command(
    title: str,
    year: int,
    quality: str,
    dir: Path,
    caption_dir: Path,
    language: list[str],
    movie_filename_tmpl: str,
    caption_filename_tmpl: str,
    caption: bool,
    caption_only: bool,
    ignore_missing_caption,
    verbose: int,
    quiet: bool,
    yes: bool,
    stream_via: bool = False,
    **download_runner_params,
):
    """Search and download or stream movie."""

    prepare_start(quiet, verbose=verbose)

    downloader = Downloader()
    get_event_loop().run_until_complete(
        downloader.download_movie(
            title,
            year=year,
            yes=yes,
            dir=dir,
            caption_dir=caption_dir,
            quality=quality.upper(),
            language=language,
            download_caption=caption,
            caption_only=caption_only,
            movie_filename_tmpl=movie_filename_tmpl,
            caption_filename_tmpl=caption_filename_tmpl,
            stream_via=stream_via,
            ignore_missing_caption=ignore_missing_caption,
            **process_download_runner_params(download_runner_params),
        )
    )


@click.command(context_settings=command_context_settings)
@click.argument("title")
@click.option(
    "-y",
    "--year",
    type=click.INT,
    help="Year filter for the series to proceed with : 0",
    default=0,
    show_default=True,
)
@click.option(
    "-s",
    "--season",
    type=click.IntRange(1, 1000),
    help="TV Series season filter",
    required=True,
    prompt="> Enter season number",
)
@click.option(
    "-e",
    "--episode",
    type=click.IntRange(1, 1000),
    help="Episode offset of the tv-series season",
    required=True,
    prompt="> Enter episode number",
)
@click.option(
    "-l",
    "--limit",
    type=click.IntRange(1, 1000),
    help="Total number of episodes to download in the season",
    default=1,
    show_default=True,
)
@click.option(
    "-q",
    "--quality",
    help="Media quality to be downloaded",
    type=click.Choice(DOWNLOAD_QUALITIES, case_sensitive=False),
    default="BEST",
    show_default=True,
)
@click.option(
    "-x",
    "--language",
    help="Caption language filter",
    multiple=True,
    default=["English"],
    show_default=True,
)
@click.option(
    "-d",
    "--dir",
    help="Directory for saving the series file to",
    type=click.Path(exists=True, file_okay=False),
    default=CURRENT_WORKING_DIR,
    show_default=True,
)
@click.option(
    "-D",
    "--caption-dir",
    help="Directory for saving the caption file to",
    type=click.Path(exists=True, file_okay=False),
    default=CURRENT_WORKING_DIR,
    show_default=True,
)
@click.option(
    "-m",
    "--mode",
    type=click.Choice(DownloadMode.map().keys(), case_sensitive=False),
    help="Start new download, resume or set automatically",
    default=DownloadMode.AUTO.value,
    show_default=True,
)
@click.option(
    "-L",
    "--episode-filename-tmpl",
    help="Template for generating series episode filename",
    default=MediaFileDownloader.series_filename_template,
    show_default=True,
)
@click.option(
    "-C",
    "--caption-filename-tmpl",
    help="Template for generating caption filename",
    default=CaptionFileDownloader.series_filename_template,
    show_default=True,
)
@click.option(
    "-t",
    "--tasks",
    type=click.IntRange(1, DEFAULT_TASKS_LIMIT),
    help="Number of tasks to carry out the download",
    default=DEFAULT_TASKS,
    show_default=True,
)
@click.option(
    "-P",
    "--part-dir",
    help="Directory for temporarily saving the downloaded file-parts to",
    type=click.Path(exists=True, file_okay=False, writable=True, resolve_path=True),
    default=CURRENT_WORKING_DIR,
    show_default=True,
)
@click.option(
    "-f",
    "--format",
    type=click.Choice(["standard", "group", "struct"]),
    default=None,
    help=(
        "Ways of formating filename and saving the episodes. "
        " group -> Organize episodes into separate folders based on seasons e.g Merlin/S1/Merlin S1E2.mp4\n"
        " struct -> Save episodes in a hierarchical directory structure e.g Merlin (2009)/S1/E1.mp4"
    ),
)
@click.option(
    "-E",
    "--part-extension",
    help="Filename extension for download parts",
    default=DOWNLOAD_PART_EXTENSION,
    show_default=True,
)
@click.option(
    "-N",
    "--chunk-size",
    type=click.INT,
    help="Streaming download chunk size in kilobytes",
    default=DEFAULT_CHUNK_SIZE,
    show_default=True,
)
@click.option(
    "-R",
    "--timeout-retry-attempts",
    type=click.INT,
    help="Number of times to retry download upon read request timing out",
    show_default=True,
    default=DEFAULT_READ_TIMEOUT_ATTEMPTS,
)
@click.option(
    "-B",
    "--merge-buffer-size",
    type=click.IntRange(1, 102400),
    help="Buffer size for merging the separated files in kilobytes [default : CHUNK_SIZE]",
    show_default=True,
)
@click.option(
    "-X",
    "--stream-via",
    type=click.Choice(media_player_name_func_map.keys()),
    default=None,
    show_default=True,
    help="Stream directly using the chosen media player instead of downloading",
)
@click.option(
    "-c",
    "--colour",
    help="Progress bar display color",
    default="cyan",
    show_default=True,
)
@click.option(
    "-U",
    "--ascii",
    is_flag=True,
    help="Use unicode (smooth blocks) to fill the progress-bar meter",
)
@click.option(
    "-z",
    "--disable-progress-bar",
    is_flag=True,
    help="Do not show download progress-bar",
)
@click.option(
    "-I",
    "--ignore-missing-caption",
    is_flag=True,
    help="Proceed to download episode file even when caption file is missing",
    show_default=True,
)
@click.option(
    "--leave/--no-leave",
    default=False,
    help="Keep all leaves of the progressbar",
    show_default=True,
)
@click.option(
    "--caption/--no-caption",
    help="Download caption file",
    default=True,
    show_default=True,
)
@click.option(
    "-O",
    "--caption-only",
    is_flag=True,
    help="Download caption file only and ignore movie",
)
@click.option(
    "-A",
    "--auto-mode",
    is_flag=True,
    help="When limit is 1 (default), download entire remaining seasons.",
)
@click.option(
    "-S",
    "--simple",
    is_flag=True,
    help="Show download percentage and bar only in progressbar",
)
@click.option(
    "-T",
    "--test",
    is_flag=True,
    help="Just test if download is possible but do not actually download",
)
@click.option(
    "-V",
    "--verbose",
    count=True,
    help="Show more detailed interactive texts",
    default=0,
)
@click.option(
    "-Q",
    "--quiet",
    is_flag=True,
    help="Disable showing interactive texts on the progress (logs)",
)
@click.option(
    "-Y",
    "--yes",
    is_flag=True,
    help="Do not prompt for tv-series confirmation",
)
@click.help_option("-h", "--help")
def download_tv_series_command(
    title: str,
    year: int,
    season: int,
    episode: int,
    limit: int,
    quality: str,
    language: list[str],
    dir: Path,
    episode_filename_tmpl: str,
    caption_filename_tmpl: str,
    caption_dir: Path,
    caption: bool,
    format: str | None,
    caption_only: bool,
    ignore_missing_caption: bool,
    verbose: int,
    quiet: bool,
    yes: bool,
    stream_via: str | None,
    auto_mode: bool,
    **download_runner_params,
):
    """Search and download or stream tv series."""

    prepare_start(quiet, verbose=verbose)

    downloader = Downloader()
    get_event_loop().run_until_complete(
        downloader.download_tv_series(
            title,
            year=year,
            season=season,
            episode=episode,
            yes=yes,
            dir=dir,
            caption_dir=caption_dir,
            quality=quality.upper(),
            language=language,
            download_caption=caption,
            caption_only=caption_only,
            limit=limit,
            episode_filename_tmpl=episode_filename_tmpl,
            caption_filename_tmpl=caption_filename_tmpl,
            stream_via=stream_via,
            ignore_missing_caption=ignore_missing_caption,
            auto_mode=auto_mode,
            format=format,
            **process_download_runner_params(download_runner_params),
        )
    )


@click.command(context_settings=command_context_settings)
@click.help_option("-h", "--help")
def interactive_menu_command():
    """Launch interactive menu interface."""
    run_interactive_menu()


def main():
    """Entry point"""
    try:
        moviebox.add_command(download_movie_command, "download-movie")
        moviebox.add_command(download_tv_series_command, "download-series")
        moviebox.add_command(mirror_hosts_command, "mirror-hosts")
        moviebox.add_command(homepage_content_command, "homepage-content")
        moviebox.add_command(popular_search_command, "popular-search")
        moviebox.add_command(item_details_command, "item-details")
        moviebox.add_command(interactive_menu_command, "interactive")
        return moviebox()

    except Exception as e:
        exception_msg = str({e.args[1] if e.args and len(e.args) > 1 else e})

        if DEBUG:
            logging.exception(e)
        else:
            if bool(exception_msg):
                logging.error(exception_msg)
            sys.exit(show_any_help(e, exception_msg))

    sys.exit(1)


if __name__ == "__main__":
    main()
