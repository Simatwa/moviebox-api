"""Commandline interface"""

import click
import os
from pathlib import Path
from asyncio import new_event_loop
from moviebox_api.constants import DOWNLOAD_QUALITIES

import logging

logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%d-%b-%Y %H:%M:%S",
    level=logging.INFO,
)

DEBUG = False  # TODO: Change this accordingly.

loop = new_event_loop()


@click.group()
def moviebox():
    """Search and download movies/series and their subtitles"""


@click.command()
@click.argument("title")
@click.option(
    "-q",
    "quality",
    help="Media quality to be downloaded",
    type=click.Choice(DOWNLOAD_QUALITIES),
    default="BEST",
)
@click.option(
    "-d",
    "--directory",
    help="Directory for saving the movie to.",
    type=click.Path(exists=True, file_okay=False),
    default=os.getcwd(),
)
@click.option("-l", "--language", help="Subtitle language filter", default="English")
@click.option("--caption/--no-caption", help="Download caption file.", default=True)
@click.option(
    "--caption-only", is_flag=True, help="Download caption file only and ignore movie."
)
@click.option("-y", "--yes", is_flag=True, help="Do not prompt for movie confirmation")
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
    """Search and download movies."""
    # TODO: Consider default moviebox host
    # TODO: Feature other download.run options
    from moviebox_api.cli.downloader import MovieDownloader

    downloader = MovieDownloader()
    loop.run_until_complete(
        downloader.download_movie(
            title,
            yes=yes,
            dir=directory,
            quality=quality,
            language=language,
            download_caption=caption,
            caption_only=caption_only,
        )
    )


def main():
    """Entry point"""
    try:
        moviebox.add_command(download_movie, "download-movie")
        moviebox()
    except Exception as e:
        if DEBUG:
            logging.exception(e)
        else:
            logging.error(f"{e.args[1] if e.args and len(e.args)>1 else e}")


if __name__ == "__main__":
    main()
