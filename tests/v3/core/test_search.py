import pytest

from moviebox_api.v3.constants import SubjectType
from moviebox_api.v3.core import Search, SearchV2
from moviebox_api.v3.http_client import MovieBoxHttpClient
from moviebox_api.v3.models.search import (
    RootSearchResultsModel,
    RootSearchResultsModelV2,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["query", "subject_type"],
    (["titanic", SubjectType.MOVIES], ["banshee", SubjectType.TV_SERIES]),
)
async def test_search_contents(query, subject_type):
    async with MovieBoxHttpClient() as client_session:
        search = Search(client_session, query, subject_type=subject_type)
        contents = await search.get_content()
        assert type(contents) is dict

        modelled_contents = await search.get_content_model()
        assert isinstance(modelled_contents, RootSearchResultsModel)

        for item in modelled_contents.items:
            assert item.subject_type is subject_type

        async for content in search.get_content_model_all():
            assert isinstance(content, RootSearchResultsModel)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["query", "subject_type"],
    (["titanic", SubjectType.MOVIES], ["banshee", SubjectType.TV_SERIES]),
)
async def test_search_contents_v2(query, subject_type):
    async with MovieBoxHttpClient() as client_session:
        search = SearchV2(client_session, query, subject_type=subject_type)
        contents = await search.get_content()
        assert type(contents) is dict

        modelled_contents = await search.get_content_model()
        assert isinstance(modelled_contents, RootSearchResultsModelV2)

        for item in modelled_contents.items:
            assert item.subject_type is subject_type

        async for content in search.get_content_model_all():
            assert isinstance(content, RootSearchResultsModelV2)


# TODO: test navigation
