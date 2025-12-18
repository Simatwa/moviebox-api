"""Contain support functions and constant variables"""

import logging
import random
import shutil
import subprocess

import click
from httpx import ConnectTimeout, HTTPStatusError
from pydantic import ValidationError
from throttlebuster import DownloadedFile, DownloadMode

from moviebox_api import __repo__, logger
from moviebox_api.constants import (
    DOWNLOAD_REQUEST_HEADERS,
    ENVIRONMENT_HOST_KEY,
    HOST_URL,
    MIRROR_HOSTS,
    SubjectType,
)
from moviebox_api.core import Search, Session
from moviebox_api.exceptions import ZeroCaptionFileError, ZeroSearchResultsError
from moviebox_api.models import (
    CaptionFileMetadata,
    DownloadableFilesMetadata,
    SearchResultsItem,
)

command_context_settings = dict(auto_envvar_prefix="MOVIEBOX")


async def perform_search_and_get_item(
    session: Session,
    title: str,
    year: int,
    subject_type: SubjectType,
    yes: bool,
    search: Search = None,
    message: str = "Select",
) -> SearchResultsItem:
    """Search movie/tv-series and return target search results item

    Args:
        session (Session): MovieboxAPI requests session.
        title (str): Partial or complete name of the movie/tv-series.
        year (int): `ReleaseDate.year` filter of the search result items.
        subject_type (SubjectType): Movie or tv-series.
        yes (bool): Proceed with the first item instead of prompting confirmation.
        search (Search, optional): Search object. Defaults to None.
        message (str, optional): Prefix message for the prompt. Defaults to "select".

    Raises:
        RuntimeError: When all items are exhausted without a match.

    Returns:
        SearchResultsItem: Targeted movie/tv-series
    """
    search = search or Search(session, title, subject_type)
    search_results = await search.get_content_model()
    subject_type_name = " ".join(subject_type.name.lower().split("_"))

    logger.info(
        f"Query '{title}' yielded {'over ' if search_results.pager.hasMore else ''}"
        f"{len(search_results.items)} {subject_type_name}."
    )
    items = (
        filter(
            lambda item: item.releaseDate.year == year,
            search_results.items,
        )
        if bool(year)
        else search_results.items
    )
    if not isinstance(items, list):
        items = [item for item in items]

    if yes:
        for item in items:
            # Just iterate once
            return item
    else:
        for pos, item in enumerate(items, start=1):
            if click.confirm(
                f"> {message} ({pos}/{len(items)}) : "
                f"{'[' + item.subjectType.name + '] ' if subject_type is SubjectType.ALL else ''}{item.title}"
                f" {item.releaseDate.year, item.imdbRatingValue}"
            ):
                return item

    if search_results.pager.hasMore:
        next_search: Search = search.next_page(search_results)
        print(f" Loading next page ({next_search._page}) ...", end="\r")

        logging.info(f"Navigating to the search results of page number {next_search._page}")
        return await perform_search_and_get_item(
            session=session,
            title=title,
            year=year,
            subject_type=subject_type,
            yes=yes,
            search=next_search,
        )

    raise RuntimeError(
        "All items in the search results are exhausted. Try researching with a different keyword"
        f"{' or different year filter.' if year > 0 else ''}"
    )


def get_caption_file_or_raise(
    downloadable_details: DownloadableFilesMetadata, language: str
) -> CaptionFileMetadata:
    """Get caption-file based on desired language or raise ValueError if it doesn't exist.

    Args:
        downloadable_details (DownloadableFilesMetadata)
        language (str): language filter such as `en` or `English`

    Raises:
        ValueError: Incase caption file for target does not exist.
        NoCaptionFileError: Incase the items lack any caption file.

    Returns:
        CaptionFileMetadata: Target caption file details
    """
    target_caption_file = downloadable_details.get_subtitle_by_language(language)

    if target_caption_file is None:
        language_subtitle_map = (
            downloadable_details.get_language_short_subtitle_map
            if len(language) == 2
            else downloadable_details.get_language_subtitle_map
        )
        subtitle_language_keys = list(language_subtitle_map().keys())

        if subtitle_language_keys:
            raise ValueError(
                f"There is no caption file for the language '{language}'. "
                f"Choose from available ones - {', '.join(list(subtitle_language_keys))}"
            )
        else:
            raise ZeroCaptionFileError(
                "The target item has no any caption file. Use --no-caption or --ignore-missing-caption flags"
                " if you're using the commandline interface to suppress this error."
            )
    return target_caption_file


def prepare_start(quiet: bool = False, verbose: int = 0) -> None:
    """Set up some stuff for better CLI usage such as:

    - Set higher logging level for some packages.
    ...

    """
    if verbose > 3:
        verbose = 2

    logging.basicConfig(
        format=("[%(asctime)s] : %(levelname)s - %(message)s" if verbose else "[%(module)s] %(message)s"),
        datefmt="%d-%b-%Y %H:%M:%S",
        level=(
            logging.ERROR
            if quiet
            # just a hack to ensure
            #           -v -> INFO
            #           -vv -> DEBUG
            else (30 - (verbose * 10))
            if verbose > 0
            else logging.INFO
        ),
    )
    logging.info(f"Using host url - {HOST_URL}")

    packages = ("httpx",)

    for package_name in packages:
        package_logger = logging.getLogger(package_name)
        package_logger.setLevel(logging.WARNING)


def process_download_runner_params(params: dict) -> dict:
    """Format parsed args from cli to required types and add extra ones

    Args:
        params (dict): Parameters for `Downloader.run`

    Returns:
        dict: Processed parameters
    """
    params["mode"] = DownloadMode.map().get(params.get("mode").lower())

    return params


def show_any_help(exception: Exception, exception_msg: str) -> int:
    """Process exception and suggest solution if exists.

    Args:
        exception (Exception): Exact exception encountered.
        exception_msg (str): Exception message

    Returns:
        int: Exit status code
    """
    exit_code = 1

    if isinstance(exception, ConnectTimeout):
        logging.info("Internet connection request has timed out. Check your connection and retry.")

    elif isinstance(exception, HTTPStatusError):
        match exception.response.status_code:
            case 403:
                logging.info(
                    "Looks like you're in a region that Moviebox doesn't offer their services to. "
                    "Use a proxy or a VPN from a different geographical location to bypass this restriction."
                )

    elif isinstance(exception, ValidationError):
        logging.info(
            "Looks like there are structural changes in the server response.\n"
            f"Report this issue at {__repo__}/issues/new"
        )

    if "404 Domain" in exception_msg:
        example_host = random.choice(MIRROR_HOSTS)
        logging.info(
            'Run "moviebox mirror-hosts" command to check available mirror hosts and '
            f'then export it to the environment using name "{ENVIRONMENT_HOST_KEY}".\n'
            f"For instance: In *nix systems you might run 'export {ENVIRONMENT_HOST_KEY}=\"{example_host}\"'"
            f' while in Windows : "set MOVIEBOX_API_HOST={example_host}'
        )

    if not isinstance(
        exception, (ValueError, AssertionError, RuntimeError, ZeroCaptionFileError, ZeroSearchResultsError)
    ):
        logging.info(f"Incase the error persist then feel free to submit the issue at {__repo__}/issues/new")

    return exit_code


def stream_video_via_mpv(url: str, subtitle_details_items: list[DownloadedFile], subtitles_dir: str):
    try:
        # Create an MPV command with properly formatted headers
        mpv_cmd = ["mpv"]
        # Disable youtube-dl/yt-dlp since we're streaming a direct video URL
        mpv_cmd.append("--no-ytdl")
        for header_name, header_value in DOWNLOAD_REQUEST_HEADERS.items():
            mpv_cmd.append(f"--http-header-fields={header_name}: {header_value}")

        for index, sub_file in enumerate(subtitle_details_items):
            if index == 0:
                mpv_cmd.append("--sid=1")
            # Convert to absolute path for mpv compatibility
            subtitle_path = sub_file.saved_to.resolve().as_posix()
            mpv_cmd.append(f"--sub-file={subtitle_path}")

        mpv_cmd.append(str(url))

        logging.info("Launching MPV with required headers and subtitles...")

        logging.debug(f"MPV launch commands :  {' '.join(mpv_cmd)}")

        subprocess.run(mpv_cmd)

        shutil.rmtree(subtitles_dir, ignore_errors=True)

        return (None, None)

    except FileNotFoundError as e:
        raise Exception(
            "MPV player not found. Please install it from https://mpv.io/installation/ "
            'to use streaming feature or retry using "--stream-via vlc" instead.'
        ) from e

    except Exception as e:
        raise Exception(f"Error launching MPV: {e}") from e


def stream_video_via_vlc(url: str, subtitle_details_items: list[DownloadedFile], subtitles_dir: str):
    try:
        user_agent = DOWNLOAD_REQUEST_HEADERS["User-Agent"]
        referrer = DOWNLOAD_REQUEST_HEADERS["Referer"]

        mpv_cmd = ["vlc", f":http-user-agent={user_agent}", f"--http-referrer={referrer}"]

        for sub_file in subtitle_details_items:
            subtitle_path = sub_file.saved_to.resolve().as_posix()
            mpv_cmd.append(f"--sub-file={subtitle_path}")

        mpv_cmd.append(str(url))

        logging.info("Launching VLC with required headers and subtitles...")

        logging.debug(f"VLC launch commands :  {' '.join(mpv_cmd)}")

        subprocess.run(mpv_cmd)

        shutil.rmtree(subtitles_dir, ignore_errors=True)

        return (None, None)

    except FileNotFoundError as e:
        raise Exception(
            "VLC media player not found. Please install it from https://www.videolan.org "
            'to use streaming feature or retry using "--stream-via mpv" instead.'
        ) from e

    except Exception as e:
        raise Exception(f"Error launching VLC: {e}") from e


media_player_name_func_map = {"mpv": stream_video_via_mpv, "vlc": stream_video_via_vlc}
