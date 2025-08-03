import pytest
from tests import MOVIE_KEYWORD
from moviebox_api import Auto


@pytest.mark.asyncio
async def test_movie_auto():
    auto = Auto()
    movie_response, caption_response = await auto.run(query=MOVIE_KEYWORD, test=True)
    assert movie_response.is_success == True
    assert caption_response.is_success == True
