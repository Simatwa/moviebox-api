"""Contain support functions and constant variables"""

import logging

import click
from httpx import ConnectTimeout, HTTPStatusError
from pydantic import ValidationError
from throttlebuster import DownloadMode

from moviebox_api import __repo__
from moviebox_api.v1.cli.helpers import (
    media_player_name_func_map,
    stream_video_via_mpv,
    stream_video_via_vlc,
)
from moviebox_api.v3 import logger
from moviebox_api.v3.constants import (
    SubjectType,
)
from moviebox_api.v3.core import Search
from moviebox_api.v3.exceptions import (
    MovieboxApiException,
    ZeroCaptionFileError,
    ZeroSearchResultsError,
)
from moviebox_api.v3.http_client import MovieBoxHttpClient
from moviebox_api.v3.models.downloadables import (
    CaptionFileMetadata,
    RootCaptionFileMetadata,
)
from moviebox_api.v3.models.search import ResultsSubjectModel

command_context_settings = dict(auto_envvar_prefix="MOVIEBOX_V3")


async def perform_search_and_get_item(
    client_session: MovieBoxHttpClient,
    title: str,
    year: int,
    subject_type: SubjectType,
    yes: bool,
    search: Search = None,
    message: str = "Select",
) -> ResultsSubjectModel:
    """Search movie/tv-series etc and return target search results item

    Args:
        client_session (MovieBoxHttpClient): MovieboxAPI http client session.
        title (str): Partial or complete name of the movie/tv-series.
        year (int): `ReleaseDate.year` filter of the search result items.
        subject_type (SubjectType): Movie, tv-series etc
        yes (bool): Proceed with the first item instead of prompting confirmation.
        search (Search, optional): Search object. Defaults to None.
        message (str, optional): Prefix message for the prompt.
            Defaults to "select".

    Raises:
        RuntimeError: When all items are exhausted without a match.

    Returns:
        ResultsSubjectModel: Target movie/tv-series
    """
    # NOTE: V3 got better way of iterating over all results item but
    # v1 implementation still works and that matters the most.
    # If you got some extra time then consider implementing using
    # `.get_content_all()`

    search = search or Search(client_session, title, subject_type)

    search_results = await search.get_content_model()
    subject_type_name = " ".join(subject_type.name.lower().split("_"))

    logger.info(
        f"Query '{title}' yielded {
            'over ' if search_results.pager.has_more else ''
        }"
        f"{len(search_results.items)} {subject_type_name}."
    )
    items = (
        filter(
            lambda item: item.release_date.year == year,
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
                f"{
                    '[' + item.subject_type.name + '] '
                    if subject_type is SubjectType.ALL
                    else ''
                }{item.title}"
                f" {item.release_date.year, item.imdb_rating_value}"
            ):
                return item

    if search_results.pager.has_more:
        next_search: Search = search.next_page(search_results)
        print(f" Loading next page ({next_search._page}) ...", end="\r")

        logging.info(
            f"Navigating to the search results of page number {next_search._page}"
        )
        return await perform_search_and_get_item(
            client_session=client_session,
            title=title,
            year=year,
            subject_type=subject_type,
            yes=yes,
            search=next_search,
            message=message,
        )

    raise RuntimeError(
        "All items in the search results are exhausted. Try researching with"
        " a different keyword"
        f"{' or different year filter.' if year > 0 else ''}"
    )


# NOTE: v3 lacks subtitle files


def get_caption_file_or_raise(
    caption_files_detail: RootCaptionFileMetadata, language: str
) -> CaptionFileMetadata:
    """Get caption-file based on desired language or raise ValueError if
    it doesn't exist.

    Args:
        caption_files_detail (RootCaptionFileMetadata)
        language (str): language filter such as `en` or `English`

    Raises:
        ValueError: Incase caption file for target does not exist.
        NoCaptionFileError: Incase the items lack any caption file.

    Returns:
        CaptionFileMetadata: Target caption file details
    """
    target_caption_file = caption_files_detail.get_subtitle_by_language(language)

    if target_caption_file is None:
        language_subtitle_map = (
            caption_files_detail.get_language_short_subtitle_map
            if len(language) == 2
            else caption_files_detail.get_language_subtitle_map
        )
        subtitle_language_keys = list(language_subtitle_map().keys())

        if subtitle_language_keys:
            raise ValueError(
                f"There is no caption file for the language '{language}'. "
                f"Choose from available ones - {
                    ', '.join(list(subtitle_language_keys))
                }"
            )
        else:
            raise ZeroCaptionFileError(
                "The target item has no any caption file. Use --no-caption or "
                "--ignore-missing-caption flags"
                " if you're using the commandline interface to suppress "
                "this error."
            )
    return target_caption_file


def prepare_start(
    quiet: bool = False,
    verbose: int = 0,
) -> None:
    """Set up some stuff for better CLI usage such as:

    - Set higher logging level for some packages.
    ...

    """
    if verbose > 3:
        verbose = 2

    logging.basicConfig(
        format=(
            "[%(asctime)s] : %(levelname)s - %(message)s"
            if verbose
            else "[%(module)s] %(message)s"
        ),
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
    # logging.info(f"Using host url - {host_url}")

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
        logging.info(
            "Internet connection request has timed out. Check your connection"
            " and retry."
        )

    elif isinstance(exception, HTTPStatusError):
        match exception.response.status_code:
            case 403:
                logging.info(
                    "Looks like you're in a region that Moviebox doesn't offer"
                    " their services to. "
                    "Use a proxy or a VPN from a different geographical location"
                    " to bypass this restriction."
                )

    elif isinstance(exception, ValidationError):
        logging.info(
            "Looks like there are structural changes in the server response.\n"
            f"Report this issue at {__repo__}/issues/new"
        )

    if not isinstance(
        exception,
        (
            ValueError,
            AssertionError,
            RuntimeError,
            # ZeroCaptionFileError,
            ZeroSearchResultsError,
        ),
    ):
        logging.info(
            "Incase the error persist then feel free to submit the issue at"
            f" {__repo__}/issues/new"
        )

    return exit_code
