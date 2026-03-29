import pytest

from moviebox_api.v1.models import SuggestedItemsModel
from moviebox_api.v2.core import (
    SearchSuggestion,
    Session,
)
from tests.v2 import MOVIE_KEYWORD


@pytest.mark.asyncio
async def test_search_suggestion():
    suggestion = SearchSuggestion(Session())
    suggestion_details = await suggestion.get_content_model(MOVIE_KEYWORD)
    assert isinstance(suggestion_details, SuggestedItemsModel)
