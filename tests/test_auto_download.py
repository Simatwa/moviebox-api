import pytest
from tests import MOVIE_KEYWORD
from moviebox_api.extra.movies import Auto


@pytest.mark.asyncio
async def test_auto_download_caption_only():
    auto = Auto()
    _, response = await auto.run(query=MOVIE_KEYWORD, caption_only=True, test=True)
    assert response.is_success


@pytest.mark.asyncio
async def test_auto_download_movie_only():
    auto = Auto(caption_language=None)
    response, _ = await auto.run(query=MOVIE_KEYWORD, test=True)
    assert response.is_success


@pytest.mark.asyncio
async def test_auto_download_movie_and_caption():
    auto = Auto()
    movie_response, caption_response = await auto.run(query=MOVIE_KEYWORD, test=True)
    assert movie_response.is_success
    assert caption_response.is_success
