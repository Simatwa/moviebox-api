"""Contains the actual console commands"""

import os
import sys
import logging
import click

from pathlib import Path

from moviebox_api import __version__
from moviebox_api.constants import DOWNLOAD_QUALITIES

from moviebox_api.cli.helpers import command_context_settings, loop
from moviebox_api.cli.helpers import (
    prepare_start,
    process_download_runner_params,
    show_any_help,
)
from moviebox_api.cli.extras import mirror_hosts, homepage_content
from moviebox_api.cli.downloader import Downloader

from moviebox_api.download import MediaFileDownloader, CaptionFileDownloader


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
    help="Year filter for the movie to proceed with : 0",
    default=0,
)
@click.option(
    "-q",
    "--quality",
    help="Media quality to be downloaded : BEST",
    type=click.Choice(DOWNLOAD_QUALITIES, case_sensitive=False),
    default="BEST",
)
@click.option(
    "-d",
    "--dir",
    help="Directory for saving the movie to : PWD",
    type=click.Path(exists=True, file_okay=False),
    default=os.getcwd(),
)
@click.option(
    "-D",
    "--caption-dir",
    help="Directory for saving the caption file to : PWD",
    type=click.Path(exists=True, file_okay=False),
    default=os.getcwd(),
)
@click.option(
    "-Z",
    "--chunk-size",
    type=click.IntRange(min=1, max=10000),
    help="Chunk-size for downloading files in KB : 512",
    default=512,
)
@click.option(
    "-m",
    "--mode",
    type=click.Choice(["START", "RESUME", "AUTO"], case_sensitive=False),
    help="Start the download, resume or set automatically : AUTO",
    default="AUTO",
)
@click.option(
    "-c",
    "--colour",
    help="Progress bar display colour : cyan",
    default="cyan",
)
@click.option(
    "-A",
    "--ascii",
    is_flag=True,
    help="Use unicode (smooth blocks) to fill the progress-bar meter : False",
)
@click.option(
    "-x",
    "--language",
    help="Caption language filter : [English]",
    multiple=True,
    default=["English"],
)
@click.option(
    "-M",
    "--movie-filename-tmpl",
    help=f"Template for generating movie filename : [default]",
    default=MediaFileDownloader.movie_filename_template,
)
@click.option(
    "-C",
    "--caption-filename-tmpl",
    help=f"Template for generating caption filename : [default]",
    default=CaptionFileDownloader.movie_filename_template,
)
@click.option(
    "--progress-bar/--no-progress-bar",
    help="Display or disable progress-bar : True",
    default=True,
)
@click.option(
    "--leave/--no-leave", default=True, help="Keep all leaves of the progressbar : True"
)
@click.option(
    "--caption/--no-caption", help="Download caption file : True", default=True
)
@click.option(
    "-O",
    "--caption-only",
    is_flag=True,
    help="Download caption file only and ignore movie : False",
)
@click.option(
    "-S",
    "--simple",
    is_flag=True,
    help="Show download percentage and bar only in progressbar : False",
)
@click.option(
    "-T",
    "--test",
    is_flag=True,
    help="Just test if download is possible but do not actually download : False",
)
@click.option(
    "-V",
    "--verbose",
    count=True,
    help="Show more detailed interactive texts : False",
    default=0,
)
@click.option(
    "-Q",
    "--quiet",
    is_flag=True,
    help="Disable showing interactive texts on the progress (logs) : False",
)
@click.option(
    "-Y", "--yes", is_flag=True, help="Do not prompt for movie confirmation : False"
)
@click.help_option("-h", "--help")
def download_movie(
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
    verbose: int,
    quiet: bool,
    yes: bool,
    **download_runner_params,
):
    """Search and download movie."""

    prepare_start(quiet, verbose=verbose)

    downloader = Downloader()
    loop.run_until_complete(
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
)
@click.option(
    "-s",
    "--season",
    type=click.IntRange(1, 1000),
    help="TV Series season filter",
    required=True,
)
@click.option(
    "-e",
    "--episode",
    type=click.IntRange(1, 1000),
    help="Episode offset of the tv-series season",
    required=True,
)
@click.option(
    "-l",
    "--limit",
    type=click.IntRange(1, 1000),
    help="Total number of episodes to download in the season : 1",
    default=1,
)
@click.option(
    "-q",
    "--quality",
    help="Media quality to be downloaded : BEST",
    type=click.Choice(DOWNLOAD_QUALITIES, case_sensitive=False),
    default="BEST",
)
@click.option(
    "-x",
    "--language",
    help="Caption language filter : [English]",
    multiple=True,
    default=["English"],
)
@click.option(
    "-d",
    "--dir",
    help="Directory for saving the series file to : PWD",
    type=click.Path(exists=True, file_okay=False),
    default=os.getcwd(),
)
@click.option(
    "-D",
    "--caption-dir",
    help="Directory for saving the caption file to : PWD",
    type=click.Path(exists=True, file_okay=False),
    default=os.getcwd(),
)
@click.option(
    "-Z",
    "--chunk-size",
    type=click.IntRange(min=1, max=10000),
    help="Chunk-size for downloading files in KB : 512",
    default=512,
)
@click.option(
    "-m",
    "--mode",
    type=click.Choice(["START", "RESUME", "AUTO"], case_sensitive=False),
    help="Start new download, resume or set automatically : AUTO",
    default="AUTO",
)
@click.option(
    "-E",
    "--episode-filename-tmpl",
    help=f"Template for generating series episode filename : [default]",
    default=MediaFileDownloader.series_filename_template,
)
@click.option(
    "-C",
    "--caption-filename-tmpl",
    help=f"Template for generating caption filename : [default]",
    default=CaptionFileDownloader.series_filename_template,
)
@click.option(
    "-c",
    "--colour",
    help="Progress bar display color : cyan",
    default="cyan",
)
@click.option(
    "-A",
    "--ascii",
    is_flag=True,
    help="Use unicode (smooth blocks) to fill the progress-bar meter : False",
)
@click.option(
    "--progress-bar/--no-progress-bar",
    help="Display or disable progress-bar : True",
    default=True,
)
@click.option(
    "--leave/--no-leave", default=True, help="Keep all leaves of the progressbar : True"
)
@click.option(
    "--caption/--no-caption", help="Download caption file : True", default=True
)
@click.option(
    "-O",
    "--caption-only",
    is_flag=True,
    help="Download caption file only and ignore movie : False",
)
@click.option(
    "-S",
    "--simple",
    is_flag=True,
    help="Show download percentage and bar only in progressbar : False",
)
@click.option(
    "-T",
    "--test",
    is_flag=True,
    help="Just test if download is possible but do not actually download : False",
)
@click.option(
    "-V",
    "--verbose",
    count=True,
    help="Show more detailed interactive texts : False",
    default=0,
)
@click.option(
    "-Q",
    "--quiet",
    is_flag=True,
    help="Disable showing interactive texts on the progress (logs) : False",
)
@click.option(
    "-Y", "--yes", is_flag=True, help="Do not prompt for tv-series confirmation : False"
)
@click.help_option("-h", "--help")
def download_tv_series(
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
    caption_only: bool,
    verbose: int,
    quiet: bool,
    yes: bool,
    **download_runner_params,
):
    """Search and download tv series."""

    prepare_start(quiet, verbose=verbose)

    downloader = Downloader()
    loop.run_until_complete(
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
            **process_download_runner_params(download_runner_params),
        )
    )


def main():
    """Entry point"""
    try:
        moviebox.add_command(download_movie, "download-movie")
        moviebox.add_command(download_tv_series, "download-series")
        moviebox.add_command(mirror_hosts, "mirror-hosts")
        moviebox.add_command(homepage_content, "homepage-content")
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
