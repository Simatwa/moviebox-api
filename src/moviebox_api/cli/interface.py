"""Contains the actual console commands"""

import click
import os
from pathlib import Path
from asyncio import new_event_loop
from moviebox_api.constants import DOWNLOAD_QUALITIES
from moviebox_api.cli.helpers import command_context_settings
from moviebox_api.cli.extras import mirror_hosts
import logging

logging.basicConfig(
    format="[%(asctime)s] : %(levelname)s - %(message)s",
    datefmt="%d-%b-%Y %H:%M:%S",
    level=logging.INFO,
)

DEBUG = os.getenv("DEBUG", "0") == "1"  # TODO: Change this accordingly.

extra_download_args = dict(test=DEBUG)

loop = new_event_loop()


@click.group()
@click.version_option("-v", "--version", package_name="moviebox-api")
def moviebox():
    """Search and download movies/series and their subtitles"""


@click.command(context_settings=command_context_settings)
@click.argument("title")
@click.option(
    "-q",
    "quality",
    help="Media quality to be downloaded : BEST",
    type=click.Choice(DOWNLOAD_QUALITIES),
    default="BEST",
)
@click.option(
    "-d",
    "--directory",
    help="Directory for saving the movie to : PWD",
    type=click.Path(exists=True, file_okay=False),
    default=os.getcwd(),
)
@click.option("-x", "--language", help="Subtitle language filter", default="English")
@click.option(
    "--caption/--no-caption", help="Download caption file. : True", default=True
)
@click.option(
    "--caption-only",
    is_flag=True,
    help="Download caption file only and ignore movie : False",
)
@click.option(
    "-y", "--yes", is_flag=True, help="Do not prompt for movie confirmation : False"
)
@click.help_option("-h", "--help")
def download_movie(
    title: str,
    quality: str,
    directory: Path,
    language: str,
    caption: bool,
    caption_only: bool,
    yes: bool,
):
    """Search and download movie."""
    # TODO: Consider default moviebox host
    # TODO: Feature other download.run options
    from moviebox_api.cli.downloader import Downloader

    from moviebox_api.cli.helpers import prepare_start

    prepare_start()

    downloader = Downloader()
    loop.run_until_complete(
        downloader.download_movie(
            title,
            yes=yes,
            dir=directory,
            quality=quality,
            language=language,
            download_caption=caption,
            caption_only=caption_only,
            **extra_download_args,
        )
    )


@click.command(context_settings=command_context_settings)
@click.argument("title")
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
    "quality",
    help="Media quality to be downloaded : BEST",
    type=click.Choice(DOWNLOAD_QUALITIES),
    default="BEST",
)
@click.option(
    "-d",
    "--directory",
    help="Directory for saving the movie to : PWD",
    type=click.Path(exists=True, file_okay=False),
    default=os.getcwd(),
)
@click.option(
    "-x", "--language", help="Subtitle language filter : English", default="English"
)
@click.option(
    "--caption/--no-caption", help="Download caption file : True", default=True
)
@click.option(
    "--caption-only",
    is_flag=True,
    help="Download caption file only and ignore series : False",
)
@click.option(
    "-y", "--yes", is_flag=True, help="Do not prompt for tv-series confirmation : False"
)
@click.help_option("-h", "--help")
def download_tv_series(
    title: str,
    season: int,
    episode: int,
    limit: int,
    quality: str,
    directory: Path,
    language: str,
    caption: bool,
    caption_only: bool,
    yes: bool,
):
    """Search and download tv series."""
    from moviebox_api.cli.downloader import Downloader
    from moviebox_api.cli.helpers import prepare_start

    prepare_start()

    downloader = Downloader()
    loop.run_until_complete(
        downloader.download_tv_series(
            title,
            season=season,
            episode=episode,
            yes=yes,
            dir=directory,
            quality=quality,
            language=language,
            download_caption=caption,
            caption_only=caption_only,
            limit=limit,
            **extra_download_args,
        )
    )


def main():
    """Entry point"""
    try:
        moviebox.add_command(download_movie, "download-movie")
        moviebox.add_command(download_tv_series, "download-series")
        moviebox.add_command(mirror_hosts, "mirror-hosts")
        moviebox()
    except Exception as e:
        if DEBUG:
            logging.exception(e)
        else:
            logging.error(f"{e.args[1] if e.args and len(e.args)>1 else e}")


if __name__ == "__main__":
    main()
