import pytest
from tests import session
from moviebox_api.core import Search
from moviebox_api.models import SearchResults


@pytest.fixture
def search():
    return Search(session=session, keyword="Titanic", per_page=4, page=1)


@pytest.mark.asyncio
async def test_get_content(search: Search):
    contents = await search.get_content()
    assert type(contents) is dict


@pytest.mark.asyncio
async def test_model_content(search: Search):
    modelled_contents = await search.get_modelled_content(latest=True)
    assert isinstance(modelled_contents, SearchResults)


@pytest.mark.asyncio
async def test_next_page_navigation(search: Search):
    next_search = search.next_page()
    await search.get_modelled_content(latest=True)
    assert isinstance(next_search, Search)


@pytest.mark.asyncio
async def test_previous_page_navigation(search: Search):
    await search.get_modelled_content(latest=True)
    next_search = search.next_page()
    await search.get_modelled_content(latest=True)
    previous_page = next_search.previous_page()
    assert isinstance(previous_page, Search)
