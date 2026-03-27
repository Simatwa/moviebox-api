import pytest

from moviebox_api import MovieAuto
from tests import MOVIE_KEYWORD


@pytest.mark.asyncio
async def test_movie_auto():
    auto = MovieAuto()
    movie_response, caption_response = await auto.run(query=MOVIE_KEYWORD, test=True)
    assert movie_response.is_success
    assert caption_response.is_success


def test_movie_auto_sync():
    auto = MovieAuto()
    movie_response, caption_response = auto.run_sync(query=MOVIE_KEYWORD, test=True)
    assert movie_response.is_success
    assert caption_response.is_success


# TODO: Make this test work

"""
@pytest.mark.asyncio
async def test_movie_auto_with_progress_hook():
    def callback_function(progress: dict):
        print(progress)
        raise RuntimeError("I don't want to coninue")

    auto = Auto(caption_language=None)
    await auto.run(query=MOVIE_KEYWORD, progress_hook=callback_function)
"""
