import pytest

from moviebox_api.core import MovieDetails, Search, SubjectType, TVSeriesDetails
from moviebox_api.models import SearchResultsModel
from moviebox_api.requests import Session
from tests import init_search


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames=["subject_type"],
    argvalues=(
        [SubjectType.ALL],
        [SubjectType.MOVIES],
        [SubjectType.TV_SERIES],
        [SubjectType.MUSIC],
    ),
)
async def test_get_content_and_model(subject_type: SubjectType):
    search: Search = init_search(Session(), subject_type=subject_type)

    contents = await search.get_content()
    assert type(contents) is dict
    modelled_contents = await search.get_content_model()

    assert isinstance(modelled_contents, SearchResultsModel)

    for item in modelled_contents.items:
        match subject_type:
            case SubjectType.MOVIES:
                assert item.subjectType == SubjectType.MOVIES
                assert isinstance(search.get_item_details(modelled_contents.first_item), MovieDetails)

            case SubjectType.TV_SERIES:
                assert item.subjectType == SubjectType.TV_SERIES
                assert isinstance(search.get_item_details(item), TVSeriesDetails)

            case "_":
                pass


@pytest.mark.asyncio
async def test_next_page_navigation():
    search = init_search(Session())
    contents = await search.get_content_model()
    assert isinstance(contents, SearchResultsModel)

    next_search = search.next_page(contents)
    assert isinstance(next_search, Search)
    next_contents = await next_search.get_content_model()

    assert isinstance(next_contents, SearchResultsModel)
    assert contents.pager.page + 1 == next_contents.pager.page


@pytest.mark.asyncio
async def test_previous_page_navigation():
    search: Search = init_search(Session(), page=3)
    contents = await search.get_content_model()
    assert isinstance(contents, SearchResultsModel)

    previous_search = search.previous_page(contents)
    assert isinstance(previous_search, Search)
    previous_contents = await previous_search.get_content_model()

    assert isinstance(previous_contents, SearchResultsModel)
    assert contents.pager.page - 1 == previous_contents.pager.page
