import pytest

from moviebox_api.v2.constants import SubjectType
from moviebox_api.v2.core import Search, SingleItemDetails, TVSeriesDetails
from moviebox_api.v2.models import SearchResultsModel, SpecificItemDetailsModel
from moviebox_api.v2.requests import Session
from tests.v2 import TV_SERIES_KEYWORD


@pytest.mark.parametrize(
    argnames=["path"],
    argvalues=(["goat-u1jZhR4CnV4"],),
)
def test_single_item_using_detail_path(path):
    session = Session()
    details = SingleItemDetails(
        session=session,
    )
    assert type(details.get_content_sync(path)) is dict
    content = details.get_content_model_sync(path)

    assert isinstance(content, SpecificItemDetailsModel)


@pytest.mark.parametrize(
    argnames=["path"],
    argvalues=(["warrior-Au4u1Uu2Nf3"],),
)
def test_tv_series_using_detail_path(path):
    session = Session()
    details = TVSeriesDetails(
        session=session,
    )

    assert type(details.get_content_sync(path)) is dict

    assert isinstance(
        details.get_content_model_sync(path), SpecificItemDetailsModel
    )


@pytest.mark.parametrize(
    argnames=["keyword", "subject_type"],
    argvalues=(
        ["Titanic", SubjectType.MOVIES],
        ["Walker", SubjectType.MUSIC],
        # ["King", SubjectType.ANIME],
        ["War", SubjectType.EDUCATION],
    ),
)
def test_single_item_using_search_results_item(
    keyword: str, subject_type: SubjectType
):
    session = Session()

    search = Search(session, query=keyword, subject_type=subject_type)

    search_results = search.get_content_model_sync()

    assert isinstance(search_results, SearchResultsModel)

    details = SingleItemDetails(
        session=session,
    )
    assert type(details.get_content_sync(search_results.first_item)) is dict

    assert isinstance(
        details.get_content_model_sync(search_results.first_item),
        SpecificItemDetailsModel,
    )


def test_tv_series_using_search_results_item():
    session = Session()
    search = Search(
        session,
        query=TV_SERIES_KEYWORD,
        subject_type=SubjectType.TV_SERIES,
    )
    search_results = search.get_content_model_sync()

    assert isinstance(search_results, SearchResultsModel)

    details = TVSeriesDetails(
        session=session,
    )
    assert (
        type(
            details.get_content_sync(
                search_results.first_item,
            )
        )
        is dict
    )

    assert isinstance(
        details.get_content_model_sync(
            search_results.first_item,
        ),
        SpecificItemDetailsModel,
    )
