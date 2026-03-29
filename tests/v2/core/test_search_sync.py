import pytest

from moviebox_api.v2.core import (
    Search,
    SubjectType,
)
from moviebox_api.v2.models import SearchResultsModel
from moviebox_api.v2.requests import Session
from tests.v2 import init_search


@pytest.mark.parametrize(
    argnames=["subject_type"],
    argvalues=(
        [SubjectType.ALL],
        [SubjectType.MOVIES],
        [SubjectType.TV_SERIES],
        [SubjectType.MUSIC],
        [SubjectType.EDUCATION],
        [SubjectType.ANIME],
    ),
)
def test_get_content_and_model(subject_type: SubjectType):
    search: Search = init_search(Session(), subject_type=subject_type)

    contents = search.get_content_sync()
    assert type(contents) is dict
    modelled_contents = search.get_content_model_sync()

    assert isinstance(modelled_contents, SearchResultsModel)
    
    if subject_type == SubjectType.ALL:
        return
    
    for item in modelled_contents.items:
        assert item.subjectType == subject_type


def test_next_page_navigation():
    search = init_search(Session())
    contents = search.get_content_model_sync()
    assert isinstance(contents, SearchResultsModel)

    next_search = search.next_page(contents)
    assert isinstance(next_search, Search)
    next_contents = next_search.get_content_model_sync()

    assert isinstance(next_contents, SearchResultsModel)
    assert contents.pager.page + 1 == next_contents.pager.page


def test_previous_page_navigation():
    search: Search = init_search(Session(), page=3)
    contents = search.get_content_model_sync()
    assert isinstance(contents, SearchResultsModel)

    previous_search = search.previous_page(contents)
    assert isinstance(previous_search, Search)
    previous_contents = previous_search.get_content_model_sync()

    assert isinstance(previous_contents, SearchResultsModel)
    assert contents.pager.page - 1 == previous_contents.pager.page
