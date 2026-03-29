import pytest

from moviebox_api.v1.models import SuggestedItemsModel
from moviebox_api.v2.core import (
    SearchSuggestion,
    Session,
)
from tests.v2 import MOVIE_KEYWORD


def test_search_suggestion():
    suggestion = SearchSuggestion(Session())
    suggestion_details = suggestion.get_content_model(MOVIE_KEYWORD)
    assert isinstance(suggestion_details, SuggestedItemsModel)
