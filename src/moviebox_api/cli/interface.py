"""Commandline interface"""

import click
import os
from pathlib import Path
from asyncio import new_event_loop

import logging

logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%d-%b-%Y %H:%M:%S",
    level=logging.INFO,
)

DEBUG = True  # TODO: Change this accordingly.

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
    type=click.Choice(["worst", "best"]),
    default="best",
)
@click.option(
    "-d",
    "--directory",
    help="Directory for saving the movie to.",
    type=click.Path(exists=True, file_okay=False),
    default=os.getcwd(),
)
@click.option("--caption/--no-caption", help="Download caption file.", default=True)
@click.option("-y", "--yes", is_flag=True, help="Do not prompt for movie confirmation")
@click.help_option("-h", "--help")
def download_movie(title: str, quality: str, directory: Path, caption: bool, yes: bool):
    """Search and download movies."""
    # TODO: Consider default moviebox host
    from moviebox_api.cli.downloader import Downloader

    downloader = Downloader()
    loop.run_until_complete(
        downloader.download_movie(
            title, yes=yes, dir=directory, quality=quality, download_caption=caption
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
            logging.error(
                f"Error occured : {e.args[1] if e.args and len(e.args)>1 else e}"
            )


if __name__ == "__main__":
    main()
