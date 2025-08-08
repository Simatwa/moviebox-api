import asyncio
from pathlib import Path

import pytest

from moviebox_api.core import Search, SubjectType
from moviebox_api.requests import Session

project_dir = Path(__file__).parent.parent

query = "Titanic"

MOVIE_KEYWORD = query

TV_SERIES_KEYWORD = "Merlin"


def init_search(
    session: Session,
    query=query,
    subject_type=SubjectType.ALL,
    per_page=4,
    page=1,
) -> Search:
    return Search(
        session=session,
        query=query,
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
