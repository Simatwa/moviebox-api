"""Contain support functions"""

import click
import logging
from moviebox_api.core import Search, Session
from moviebox_api.constants import SubjectType
from moviebox_api import logger
from moviebox_api.models import DownloadableFilesMetadata
from moviebox_api.constants import host_url, DownloadMode

command_context_settings = dict(auto_envvar_prefix="MOVIEBOX")


async def perform_search_and_get_item(
    session: Session,
    title: str,
    subject_type: SubjectType,
    yes: bool,
):
    """Search movie/tv-series and return target search results item"""
    search = Search(session, title, subject_type)
    search_results = await search.get_modelled_content()
    subject_type_name = " ".join(subject_type.name.lower().split("_"))
    logger.info(
        f"Query '{title}' yielded {len(search_results.items)} {subject_type_name}."
    )

    if yes:
        return search_results.first_item
    else:
        for item in search_results.items:
            if click.confirm(f"> Download {item.title} ({item.releaseDate.year})"):
                return item
    raise RuntimeError(
        "All items in the search results are exhausted. Try researching with different keyword."
    )


def get_caption_file_or_raise(
    downloadable_details: DownloadableFilesMetadata, language: str
):
    """Returns caption-file based on desired language or raise ValueError if it doesn't exist."""
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


def prepare_start():
    """Set up some stuff for better CLI usage such as:

    - Set higher logging level for some packages.
    ...

    """
    logging.info(f"Using host url - {host_url}")
    packages = ("httpx",)
    for package_name in packages:
        package_logger = logging.getLogger(package_name)
        package_logger.setLevel(logging.WARNING)


def process_download_runner_params(params: dict):
    params["mode"] = DownloadMode.map_cls().get(params.get("mode").lower())
    return params
