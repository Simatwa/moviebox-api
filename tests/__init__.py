import pytest
import asyncio
from moviebox_api.requests import Session
from moviebox_api.core import Search
from moviebox_api.core import SubjectType

keyword = "Titanic"

MOVIE_KEYWORD = keyword

TV_SERIES_KEYWORD = "Merlin"


def init_search(
    session=Session(), keyword=keyword, subject_type=SubjectType.ALL, per_page=4, page=1
) -> Search:
    return Search(
        session=session,
        keyword=keyword,
        subject_type=subject_type,
        per_page=per_page,
        page=page,
    )


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()
