import pytest

from moviebox_api.v3.core import Homepage
from moviebox_api.v3.http_client import MovieBoxHttpClient
from moviebox_api.v3.models.homepage import RootHomepageModel


@pytest.mark.asyncio
async def test_homepage_fetch_contents():
    async with MovieBoxHttpClient() as client_session:
        homepage = Homepage(client_session)
        contents = await homepage.get_content()
        assert type(contents) is dict
        modelled_contents = await homepage.get_content_model()
        assert isinstance(modelled_contents, RootHomepageModel)
