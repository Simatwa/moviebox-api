import pytest
from pydantic import BaseModel

from moviebox_api import Search, Session, SubjectType
from moviebox_api.core import (
    HotMoviesAndTVSeries,
    PopularSearch,
    Recommend,
    SearchSuggestion,
    Trending,
)
from tests import MOVIE_KEYWORD


@pytest.mark.asyncio
async def test_popular_search():
    search = PopularSearch(Session())
    assert type(await search.get_content()) is list
    modelled_content = await search.get_content_model()
    assert isinstance(modelled_content[0], BaseModel)


@pytest.mark.asyncio
async def test_recommend():
    session = Session()

    search = Search(session, query=MOVIE_KEYWORD, subject_type=SubjectType.MOVIES)
    search_results = await search.get_content_model()
    target_item = search_results.first_item

    recommend = Recommend(session, item=target_item)
    recommendeded_details = await recommend.get_content_model()
    assert isinstance(recommendeded_details, BaseModel)

    next_recommend = recommend.next_page(recommendeded_details)
    assert isinstance(next_recommend, Recommend)
    next_recommended_details = await next_recommend.get_content_model()

    assert isinstance(next_recommended_details, BaseModel)
    previous_recommend = next_recommend.previous_page(next_recommended_details)
    assert isinstance(previous_recommend, Recommend)

    assert next_recommend._page > recommend._page
    assert previous_recommend._page == recommend._page


@pytest.mark.asyncio
async def test_search_suggestion():
    suggestion = SearchSuggestion(Session())
    suggestion_details = await suggestion.get_content_model(MOVIE_KEYWORD)
    assert isinstance(suggestion_details, BaseModel)


@pytest.mark.asyncio
async def test_hot_movies_and_series():
    hot_movies_and_series = HotMoviesAndTVSeries(Session())
    hot_item_details = await hot_movies_and_series.get_content_model()
    assert isinstance(hot_item_details, BaseModel)


@pytest.mark.asyncio
async def test_trending():
    trending = Trending(Session())

    trending_items = await trending.get_content_model()
    assert isinstance(trending_items, BaseModel)
    next_trends = trending.next_page(trending_items)

    assert isinstance(next_trends, Trending)
    assert next_trends._page > trending._page
    next_trending_items = await next_trends.get_content_model()

    assert isinstance(next_trending_items, BaseModel)
    previous_trends = next_trends.previous_page(next_trending_items)
    assert isinstance(previous_trends, Trending)

    assert previous_trends._page == trending._page
    previous_trending_items = await previous_trends.get_content_model()
    assert isinstance(previous_trending_items, BaseModel)
