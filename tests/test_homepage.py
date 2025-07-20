import pytest
from moviebox_api.core import Homepage
from moviebox_api.models import HomepageContentModel
from moviebox_api.requests import Session


@pytest.mark.asyncio
async def test_homepage():
    """Tests homepage content fetching and modelling it"""
    homepage = Homepage(session=Session())
    contents = await homepage.get_content()
    assert type(contents) is dict
    modelled_contents = await homepage.get_modelled_content()
    assert isinstance(modelled_contents, HomepageContentModel)
