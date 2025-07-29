import click
from moviebox_api.core import Search, Session
from moviebox_api.constants import SubjectType
from moviebox_api import logger
from moviebox_api.models import DownloadableFilesMetadata

async def perform_search_and_get_item(session: Session, title: str, subject_type: SubjectType, yes:bool, ):
    search = Search(session, title, subject_type)
    search_results = await search.get_modelled_content()
    logger.info(f"Query '{title}' yielded {len(search_results.items)} search results.")

    if yes:
            return search_results.first_item
    else:
            for tv_series in search_results.items:
                if click.confirm(f"Download {tv_series.title} ({tv_series.releaseDate.year})"):
                    return tv_series
    raise RuntimeError(
                "All items in the search results are exhausted. Try researching with different keyword."
            )

def get_caption_file_or_raise(downloadable_details:DownloadableFilesMetadata, language:str):
            target_caption_file = downloadable_details.get_subtitle_by_language(
                language
            )
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