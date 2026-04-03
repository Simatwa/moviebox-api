import pytest
from pydantic import BaseModel

from moviebox_api.v1.constants import SubjectType
from moviebox_api.v1.core import MovieDetails, Search, TVSeriesDetails
from moviebox_api.v1.extractor import (
    JsonDetailsExtractor,
    JsonDetailsExtractorModel,
    TagDetailsExtractor,
    TagDetailsExtractorModel,
)
from moviebox_api.v1.requests import Session
from tests.v1 import (
    MOVIE_KEYWORD,
    TEST_MOVIE_PAGE_URL,
    TEST_TV_SERIES_PAGE_URL,
    TV_SERIES_KEYWORD,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames=["url"],
    argvalues=(
        [TEST_MOVIE_PAGE_URL],
        [
            TEST_TV_SERIES_PAGE_URL,
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

    assert isinstance(
        await details.get_json_details_extractor(), JsonDetailsExtractor
    )
    assert isinstance(
        await details.get_tag_details_extractor(), TagDetailsExtractor
    )

    assert isinstance(
        await details.get_json_details_extractor_model(),
        JsonDetailsExtractorModel,
    )
    assert isinstance(
        await details.get_tag_details_extractor_model(), TagDetailsExtractorModel
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames=["url"],
    argvalues=(["/detail/county-49-UcSx2qEJvw7?id=6315211642355729232"],),
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

    assert isinstance(
        await details.get_json_details_extractor(), JsonDetailsExtractor
    )
    assert isinstance(
        await details.get_tag_details_extractor(), TagDetailsExtractor
    )

    assert isinstance(
        await details.get_json_details_extractor_model(),
        JsonDetailsExtractorModel,
    )
    assert isinstance(
        await details.get_tag_details_extractor_model(), TagDetailsExtractorModel
    )


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

    assert isinstance(
        await details.get_json_details_extractor(), JsonDetailsExtractor
    )
    assert isinstance(
        await details.get_tag_details_extractor(), TagDetailsExtractor
    )

    assert isinstance(
        await details.get_json_details_extractor_model(),
        JsonDetailsExtractorModel,
    )
    assert isinstance(
        await details.get_tag_details_extractor_model(), TagDetailsExtractorModel
    )


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

    assert isinstance(
        await details.get_json_details_extractor(), JsonDetailsExtractor
    )
    assert isinstance(
        await details.get_tag_details_extractor(), TagDetailsExtractor
    )

    assert isinstance(
        await details.get_json_details_extractor_model(),
        JsonDetailsExtractorModel,
    )
    assert isinstance(
        await details.get_tag_details_extractor_model(), TagDetailsExtractorModel
    )
