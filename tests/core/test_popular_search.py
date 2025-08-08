import pytest
from pydantic import BaseModel

from moviebox_api import PopularSearch, Session


@pytest.mark.asyncio
async def test_popular_search():
    search = PopularSearch(Session())
    assert type(await search.get_content()) is dict
    assert isinstance(await search.get_content_model(), BaseModel)
