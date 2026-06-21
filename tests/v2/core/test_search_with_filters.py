import pytest

from moviebox_api.v2.core import (
    SearchWithFilter,
    SubjectType,
)
from moviebox_api.v2.models import SearchResultsModel
from moviebox_api.v2.types import FilterParams


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames=["subject_type", "filter_params", "page_number", "per_page"],
    argvalues=(
        [SubjectType.MOVIES, FilterParams(), 1, 2],
        [SubjectType.TV_SERIES, FilterParams(), 2, 2],
        [SubjectType.MOVIES, FilterParams(sort="Hottest"), 3, 2],
        [SubjectType.TV_SERIES, FilterParams(genre="Documentary"), 6, 2],
    ),
)
async def test_get_content_and_model(
    subject_type: SubjectType, filter_params: FilterParams, page_number, per_page
):
    search: SearchWithFilter = SearchWithFilter(
        subject_type=subject_type,
        filter_params=filter_params,
        page=page_number,
        per_page=per_page,
    )

    contents = await search.get_content()
    assert type(contents) is dict
    modelled_contents = await search.get_content_model()

    assert isinstance(modelled_contents, SearchResultsModel)

    for item in modelled_contents.items:
        assert item.subjectType == subject_type


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames=["subject_type", "filter_params", "page_number", "per_page"],
    argvalues=(
        [SubjectType.ANIME, FilterParams(), 1, 2],
        [SubjectType.ANIME, FilterParams(country="United Kingdom"), 2, 2],
        [SubjectType.ANIME, FilterParams(sort="Hottest"), 3, 2],
        [SubjectType.ANIME, FilterParams(genre="Documentary"), 6, 2],
    ),
)
async def test_get_content_and_model_anime(
    subject_type: SubjectType, filter_params: FilterParams, page_number, per_page
):
    search: SearchWithFilter = SearchWithFilter(
        subject_type=subject_type,
        filter_params=filter_params,
        page=page_number,
        per_page=per_page,
    )

    contents = await search.get_content()
    assert type(contents) is dict
    modelled_contents = await search.get_content_model()

    assert isinstance(modelled_contents, SearchResultsModel)

    for item in modelled_contents.items:
        assert item.subjectType == subject_type


@pytest.mark.asyncio
@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames=["subject_type", "filter_params", "page_number", "per_page"],
    argvalues=(
        [SubjectType.ANIME, FilterParams(), 2, 2],
        [SubjectType.MOVIES, FilterParams(country="Kenya"), 2, 2],
        [SubjectType.TV_SERIES, FilterParams(sort="Latest"), 4, 2],
        [SubjectType.MOVIES, FilterParams(genre="Action"), 5, 2],
        [SubjectType.TV_SERIES, FilterParams(language="Indonesian dub"), 1, 2],
    ),
)
async def test_next_page_navigation(
    subject_type: SubjectType, filter_params: FilterParams, page_number, per_page
):
    search: SearchWithFilter = SearchWithFilter(
        subject_type=subject_type,
        filter_params=filter_params,
        page=page_number,
        per_page=per_page,
    )
    contents = await search.get_content_model()
    assert isinstance(contents, SearchResultsModel)

    next_search = search.next_page(contents)
    assert isinstance(next_search, SearchWithFilter)
    next_contents = await next_search.get_content_model()

    assert isinstance(next_contents, SearchResultsModel)
    assert contents.pager.page + 1 == next_contents.pager.page


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames=["subject_type", "filter_params", "page_number", "per_page"],
    argvalues=(
        [SubjectType.ANIME, FilterParams(), 3, 2],
        [SubjectType.MOVIES, FilterParams(sort="Rating"), 4, 2],
        [SubjectType.TV_SERIES, FilterParams(language="English dub"), 4, 2],
        [SubjectType.MOVIES, FilterParams(country="Germany"), 3, 2],
        [SubjectType.TV_SERIES, FilterParams(year="2020"), 5, 2],
    ),
)
async def test_previous_page_navigation(
    subject_type: SubjectType, filter_params: FilterParams, page_number, per_page
):
    search: SearchWithFilter = SearchWithFilter(
        subject_type=subject_type,
        filter_params=filter_params,
        page=page_number,
        per_page=per_page,
    )
    contents = await search.get_content_model()
    assert isinstance(contents, SearchResultsModel)

    previous_search = search.previous_page(contents)
    assert isinstance(previous_search, SearchWithFilter)
    previous_contents = await previous_search.get_content_model()

    assert isinstance(previous_contents, SearchResultsModel)
    assert contents.pager.page - 1 == previous_contents.pager.page


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames=["subject_type", "filter_params", "page_number", "per_page"],
    argvalues=(
        [SubjectType.MOVIES, FilterParams(sort="Rating"), 4, 2],
        [SubjectType.TV_SERIES, FilterParams(language="English dub"), 4, 2],
        [SubjectType.MOVIES, FilterParams(country="Germany"), 3, 2],
        [SubjectType.TV_SERIES, FilterParams(year="2020"), 5, 2],
    ),
)
async def test_continous_navigation(
    subject_type: SubjectType, filter_params: FilterParams, page_number, per_page
):
    search: SearchWithFilter = SearchWithFilter(
        subject_type=subject_type,
        filter_params=filter_params,
        page=page_number,
        per_page=per_page,
    )
    iterations_limit = 5
    iterations_count = 0

    async for results in search.get_content_model_all():
        iterations_count += 1
        assert isinstance(results, SearchResultsModel)
        if iterations_count == iterations_limit:
            break
