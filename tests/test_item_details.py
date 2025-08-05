import pytest

from moviebox_api.core import MovieDetails, TVSeriesDetails
from moviebox_api.requests import Session
from moviebox_api.constants import SubjectType
from moviebox_api.core import Search
from tests import TV_SERIES_KEYWORD, MOVIE_KEYWORD


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames=["url"],
    argvalues=(
        ["https://moviebox.pk/detail/titanic-m7a9yt0abq6?id=5390197429792821032"],
        [
            "/detail/titanic-m7a9yt0abq6?id=5390197429792821032",
        ],
    ),
)
async def test_movie_using_page_url(url):
    session = Session()
    details = MovieDetails(
        url,
        session=session,
    )
    extracts = await details.get_json_extractor()
    assert type(extracts.resources_and_reviews) is dict


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames=["url"],
    argvalues=(
        [
            "https://moviebox.pk/detail/merlin-sMxCiIO6fZ9?id=8382755684005333552&scene&page_from=search_detail&type=%2Fmovie%2Fdetail"
        ],
        [
            "https://moviebox.pk/detail/merlin-sMxCiIO6fZ9?id=8382755684005333552",
        ],
    ),
)
async def test_tv_series_using_page_url(url):
    session = Session()
    details = TVSeriesDetails(
        url,
        session=session,
    )
    extracts = await details.get_json_extractor()
    assert type(extracts.resources_and_reviews) is dict


@pytest.mark.asyncio
async def test_movie_using_search_results_item():
    session = Session()
    search = Search(session, keyword=MOVIE_KEYWORD, subject_type=SubjectType.MOVIES)
    search_results = await search.get_modelled_content()
    details = MovieDetails(
        search_results.first_item,
        session=session,
    )
    extracts = await details.get_json_extractor()
    assert type(extracts.resources_and_reviews) is dict


@pytest.mark.asyncio
async def test_tv_series_using_search_results_item():
    session = Session()
    search = Search(
        session, keyword=TV_SERIES_KEYWORD, subject_type=SubjectType.TV_SERIES
    )
    search_results = await search.get_modelled_content()
    details = TVSeriesDetails(
        search_results.first_item,
        session=session,
    )
    extracts = await details.get_json_extractor()
    assert type(extracts.resources_and_reviews) is dict
