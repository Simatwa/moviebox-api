import pytest
from pydantic import BaseModel

from moviebox_api.constants import SubjectType
from moviebox_api.core import MovieDetails, Search, TVSeriesDetails
from moviebox_api.extractor import (
    JsonDetailsExtractor,
    JsonDetailsExtractorModel,
    TagDetailsExtractor,
    TagDetailsExtractorModel,
)
from moviebox_api.requests import Session
from tests import MOVIE_KEYWORD, TV_SERIES_KEYWORD


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
    assert type(await details.get_html_content()) is str
    assert type(await details.get_content()) is dict
    assert isinstance(await details.get_content_model(), BaseModel)

    assert isinstance(await details.get_json_details_extractor(), JsonDetailsExtractor)
    assert isinstance(await details.get_tag_details_extractor(), TagDetailsExtractor)

    assert isinstance(await details.get_json_details_extractor_model(), JsonDetailsExtractorModel)
    assert isinstance(await details.get_tag_details_extractor_model(), TagDetailsExtractorModel)


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
    assert type(await details.get_html_content()) is str
    assert type(await details.get_content()) is dict
    assert isinstance(await details.get_content_model(), BaseModel)

    assert isinstance(await details.get_json_details_extractor(), JsonDetailsExtractor)
    assert isinstance(await details.get_tag_details_extractor(), TagDetailsExtractor)

    assert isinstance(await details.get_json_details_extractor_model(), JsonDetailsExtractorModel)
    assert isinstance(await details.get_tag_details_extractor_model(), TagDetailsExtractorModel)


@pytest.mark.asyncio
async def test_movie_using_search_results_item():
    session = Session()
    search = Search(session, query=MOVIE_KEYWORD, subject_type=SubjectType.MOVIES)
    search_results = await search.get_content_model()
    details = MovieDetails(
        search_results.first_item,
        session=session,
    )
    assert type(await details.get_html_content()) is str
    assert type(await details.get_content()) is dict
    assert isinstance(await details.get_content_model(), BaseModel)

    assert isinstance(await details.get_json_details_extractor(), JsonDetailsExtractor)
    assert isinstance(await details.get_tag_details_extractor(), TagDetailsExtractor)

    assert isinstance(await details.get_json_details_extractor_model(), JsonDetailsExtractorModel)
    assert isinstance(await details.get_tag_details_extractor_model(), TagDetailsExtractorModel)


@pytest.mark.asyncio
async def test_tv_series_using_search_results_item():
    session = Session()
    search = Search(
        session,
        query=TV_SERIES_KEYWORD,
        subject_type=SubjectType.TV_SERIES,
    )
    search_results = await search.get_content_model()
    details = TVSeriesDetails(
        search_results.first_item,
        session=session,
    )
    assert type(await details.get_html_content()) is str
    assert type(await details.get_content()) is dict
    assert isinstance(await details.get_content_model(), BaseModel)

    assert isinstance(await details.get_json_details_extractor(), JsonDetailsExtractor)
    assert isinstance(await details.get_tag_details_extractor(), TagDetailsExtractor)

    assert isinstance(await details.get_json_details_extractor_model(), JsonDetailsExtractorModel)
    assert isinstance(await details.get_tag_details_extractor_model(), TagDetailsExtractorModel)
