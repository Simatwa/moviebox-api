import pytest

from moviebox_api.v1.models import SuggestedItemsModel
from moviebox_api.v2.core import (
    ContentCategory,
    Homepage,
    MoviesOperatingList,
    SearchSuggestion,
    Session,
)
from moviebox_api.v2.models import HomepageContentModel, RealContentCategoryModel
from tests.v2 import MOVIE_KEYWORD


@pytest.mark.asyncio
async def test_search_suggestion():
    suggestion = SearchSuggestion(Session())
    suggestion_details = await suggestion.get_content_model(MOVIE_KEYWORD)
    assert isinstance(suggestion_details, SuggestedItemsModel)


@pytest.mark.asyncio
async def test_homepage():
    home = Homepage(session=Session())
    content = await home.get_content()
    assert type(content) is dict

    modelled_content = await home.get_content_model()
    assert isinstance(modelled_content, HomepageContentModel)


@pytest.mark.asyncio
async def test_movies_operating_list():
    ops = MoviesOperatingList(session=Session())
    content = await ops.get_content()
    assert type(content) is dict

    modelled_content = await ops.get_content_model()
    assert isinstance(modelled_content, HomepageContentModel)


@pytest.mark.asyncio
async def test_content_category_from_homepage():
    session = Session()
    home = Homepage(session=session)
    content = await home.get_content_model()

    ops_list_limit = 3

    for ops_list_count, ops_list in enumerate(content.operatingList, start=1):
        if not ops_list.genreTopId:
            print(f"Skipping ops_list due to missing genreTopId {ops_list=}")

            ops_list_limit += 1
            continue

        cat = ContentCategory(
            genre_top_id=ops_list.genreTopId,
            session=session,
        )

        content = await cat.get_content()
        assert type(content) is dict

        modelled_content = await cat.get_content_model()
        assert isinstance(modelled_content, RealContentCategoryModel)

        # test navigation

        # next-page

        next = cat.next_page(modelled_content)
        next_modelled_content = await next.get_content_model()
        assert isinstance(next_modelled_content, RealContentCategoryModel)

        # prev-page

        prev_page = cat.previous_page(next_modelled_content)
        prev_page_modelled_content = await prev_page.get_content_model()
        assert prev_page_modelled_content == modelled_content

        # test continuous navigation

        cont_page_limit = 2
        cont_page_count = 0

        async for cont_modelled_content in prev_page.get_content_model_all():
            cont_page_count += 1
            assert isinstance(cont_modelled_content, RealContentCategoryModel)

            if cont_page_count == cont_page_limit:
                break

        if ops_list_count == ops_list_limit:
            break
