"""Contains the actual console commands"""

import click
import os
from pathlib import Path
from asyncio import new_event_loop
from moviebox_api.constants import DOWNLOAD_QUALITIES, DownloadMode
from moviebox_api.cli.helpers import command_context_settings
from moviebox_api.cli.helpers import prepare_start, process_download_runner_params
from moviebox_api.cli.extras import mirror_hosts
import logging

logging.basicConfig(
    format="[%(asctime)s] : %(levelname)s - %(message)s",
    datefmt="%d-%b-%Y %H:%M:%S",
    level=logging.INFO,
)

DEBUG = os.getenv("DEBUG", "0") == "1"  # TODO: Change this accordingly.

loop = new_event_loop()


@click.group()
@click.version_option("-v", "--version", package_name="moviebox-api")
def moviebox():
    """Search and download movies/series and their subtitles. envvar_prefix : MOVIEBOX"""


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
    "--dir",
    help="Directory for saving the movie to : PWD",
    type=click.Path(exists=True, file_okay=False),
    default=os.getcwd(),
)
@click.option(
    "-cd",
    "--caption-dir",
    help="Directory for saving the caption file to : PWD",
    type=click.Path(exists=True, file_okay=False),
    default=os.getcwd(),
)
@click.option(
    "-cs",
    "--chunk-size",
    type=click.IntRange(min=1, max=10000),
    help="Chunk_size for downloading files in KB - 512",
    default=512,
)
@click.option(
    "-m",
    "--mode",
    type=click.Choice(["START", "RESUME", "AUTO"], case_sensitive=False),
    help="Start the download, resume or set automatically - AUTO",
    default="AUTO",
)
@click.option(
    "--leave/--no-leave", default=True, help="Keep all leaves of the progressbar : True"
)
@click.option(
    "-c",
    "--colour",
    help="Progress bar display colour : cyan",
    default="cyan",
)
@click.option(
    "-ac",
    "--ascii",
    is_flag=True,
    help="Use unicode (smooth blocks) to fill the progress-bar meter : False",
)
@click.option(
    "-t",
    "--test",
    is_flag=True,
    help="Just test if download is possible but do not actually download : False",
)
@click.option(
    "-x",
    "--language",
    help="Subtitle language filter",
    multiple=True,
    default=["English"],
)
@click.option(
    "--caption/--no-caption", help="Download caption file. : True", default=True
)
@click.option(
    "--caption-only",
    is_flag=True,
    help="Download caption file only and ignore movie : False",
)
@click.option(
    "-qu",
    "--quiet",
    is_flag=True,
    help="Do not show download progressbar : False",
)
@click.option(
    "-y", "--yes", is_flag=True, help="Do not prompt for movie confirmation : False"
)
@click.help_option("-h", "--help")
def download_movie(
    title: str,
    quality: str,
    dir: Path,
    caption_dir: Path,
    language: list[str],
    caption: bool,
    caption_only: bool,
    yes: bool,
    **download_runner_params,
):
    """Search and download movie."""
    from moviebox_api.cli.downloader import Downloader

    prepare_start()

    downloader = Downloader()
    loop.run_until_complete(
        downloader.download_movie(
            title,
            yes=yes,
            dir=dir,
            caption_dir=caption_dir,
            quality=quality,
            language=language,
            download_caption=caption,
            caption_only=caption_only,
            **process_download_runner_params(download_runner_params),
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
    "--quality",
    help="Media quality to be downloaded : BEST",
    type=click.Choice(DOWNLOAD_QUALITIES),
    default="BEST",
)
@click.option(
    "-x",
    "--language",
    help="Subtitle language filter",
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
    "-cd",
    "--caption-dir",
    help="Directory for saving the caption file to : PWD",
    type=click.Path(exists=True, file_okay=False),
    default=os.getcwd(),
)
@click.option(
    "-cs",
    "--chunk-size",
    type=click.IntRange(min=1, max=10000),
    help="Chunk_size for downloading files in KB - 512",
    default=512,
)
@click.option(
    "-m",
    "--mode",
    type=click.Choice(["START", "RESUME", "AUTO"], case_sensitive=False),
    help="Start new download, resume or set automatically - AUTO",
    default="AUTO",
)
@click.option(
    "--leave/--no-leave", default=True, help="Keep all leaves of the progressbar : True"
)
@click.option(
    "-c",
    "--colour",
    help="Progress bar display color : cyan",
    default="cyan",
)
@click.option(
    "-ac",
    "--ascii",
    is_flag=True,
    help="Use unicode (smooth blocks) to fill the progress-bar meter : False",
)
@click.option(
    "-t",
    "--test",
    is_flag=True,
    help="Just test if download is possible but do not actually download : False",
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
    "-qu",
    "--quiet",
    is_flag=True,
    help="Do not show download progressbar : False",
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
    language: list[str],
    dir: Path,
    caption_dir: Path,
    caption: bool,
    caption_only: bool,
    yes: bool,
    **download_runner_params,
):
    """Search and download tv series."""
    from moviebox_api.cli.downloader import Downloader

    prepare_start()

    downloader = Downloader()
    loop.run_until_complete(
        downloader.download_tv_series(
            title,
            season=season,
            episode=episode,
            yes=yes,
            dir=dir,
            caption_dir=caption_dir,
            quality=quality,
            language=language,
            download_caption=caption,
            caption_only=caption_only,
            limit=limit,
            **process_download_runner_params(download_runner_params),
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
