import click
from moviebox_api.core import Search, Session
from moviebox_api.constants import SubjectType
from moviebox_api import logger


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
