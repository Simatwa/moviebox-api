"""Contain support functions and constant variables"""

import click
import logging

from moviebox_api import logger
from moviebox_api.core import Search, Session
from moviebox_api.constants import SubjectType
from moviebox_api.constants import HOST_URL, DownloadMode
from moviebox_api.models import DownloadableFilesMetadata
from moviebox_api.models import SearchResultsItem, CaptionFileMetadata


command_context_settings = dict(auto_envvar_prefix="MOVIEBOX")


async def perform_search_and_get_item(
    session: Session,
    title: str,
    year: int,
    subject_type: SubjectType,
    yes: bool,
    search: Search = None,
) -> SearchResultsItem:
    """Search movie/tv-series and return target search results item

    Args:
        session (Session): MovieboxAPI requests session.
        title (str): Partial or complete name of the movie/tv-series.
        year (int): `ReleaseDate.year` filter of the search result items.
        subject_type (SubjectType): Movie or tv-series.
        yes (bool): Proceed with the first item instead of prompting confirmation.
        search (Search, optional): Search object. Defaults to None.

    Raises:
        RuntimeError: When all items are exhausted without a match.

    Returns:
        SearchResultsItem: Targeted movie/tv-series
    """
    search = search or Search(session, title, subject_type)
    search_results = await search.get_modelled_content()
    subject_type_name = " ".join(subject_type.name.lower().split("_"))
    logger.info(
        f"Query '{title}' yielded {'over ' if search_results.pager.hasMore else ''}"
        f"{len(search_results.items)} {subject_type_name}."
    )
    items = (
        filter(lambda item: item.releaseDate.year == year, search_results.items)
        if year > 0
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
                f"> Download ({pos}/{len(items)}) : {item.title} {item.releaseDate.year, item.imdbRatingValue}"
            ):
                return item
    if search_results.pager.hasMore:
        next_search: Search = search.next_page(search_results)
        logging.info(
            f"Navigating to the search results of page number {next_search._page}"
        )
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
        f'{" or different year filter." if year > 0 else ""}'
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
        raise ValueError(
            f"There is no caption file for the language '{language}'. "
            f"Choose from available ones - {', '.join(list(language_subtitle_map().keys()))}"
        )
    return target_caption_file


def prepare_start(quiet: bool, verbose: bool) -> None:
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
            else (30 - (verbose * 10)) if verbose > 0 else logging.INFO
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
    params["mode"] = DownloadMode.map_cls().get(params.get("mode").lower())
    params["suppress_complete_error"] = True
    return params
