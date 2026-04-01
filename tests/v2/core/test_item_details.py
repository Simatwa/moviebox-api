import pytest
from pydantic import BaseModel

from moviebox_api.v2.constants import SubjectType
from moviebox_api.v2.core import Search, SingleItemDetails, TVSeriesDetails
from moviebox_api.v2.models import SearchResultsModel, SpecificItemDetailsModel
from moviebox_api.v2.requests import Session
from tests.v2 import MOVIE_KEYWORD, TV_SERIES_KEYWORD


@pytest.mark.asynciok
@pytest.mark.parametrize(
    argnames=["path"],
    argvalues=(["goat-u1jZhR4CnV4"],),
)
async def test_single_item_using_detail_path(path):
    session = Session()
    details = SingleItemDetails(
        session=session,
    )
    assert type(await details.get_content(path)) is dict
    content = await details.get_content_model(path)

    assert isinstance(content, SpecificItemDetailsModel)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames=["path"],
    argvalues=(["warrior-Au4u1Uu2Nf3"],),
)
async def test_tv_series_using_detail_path(path):
    session = Session()
    details = TVSeriesDetails(
        session=session,
    )

    assert type(await details.get_content(path)) is dict

    assert isinstance(
        await details.get_content_model(path), SpecificItemDetailsModel
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames=["keyword", "subject_type"],
    argvalues=(
        ["Titanic", SubjectType.MOVIES],
        ["Walker", SubjectType.MUSIC],
        # ["King", SubjectType.ANIME],
        ["War", SubjectType.EDUCATION],
    ),
)
async def test_single_item_using_search_results_item(
    keyword: str, subject_type: SubjectType
):
    session = Session()

    search = Search(session, query=keyword, subject_type=subject_type)

    search_results = await search.get_content_model()

    assert isinstance(search_results, SearchResultsModel)

    details = SingleItemDetails(
        session=session,
    )
    assert type(await details.get_content(search_results.first_item)) is dict

    assert isinstance(
        await details.get_content_model(search_results.first_item),
        SpecificItemDetailsModel,
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

    assert isinstance(search_results, SearchResultsModel)

    details = TVSeriesDetails(
        session=session,
    )
    assert (
        type(
            await details.get_content(
                search_results.first_item,
            )
        )
        is dict
    )

    assert isinstance(
        await details.get_content_model(
            search_results.first_item,
        ),
        SpecificItemDetailsModel,
    )
