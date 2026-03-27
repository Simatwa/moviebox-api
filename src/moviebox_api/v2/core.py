"""
Main module for the package.
Generate models from httpx request responses.
Also provides object mapping support to specific extracted item details
"""

import moviebox_api.v1.core
from moviebox_api.v2._bases import BaseSearch
from moviebox_api.v2.helpers import get_absolute_url
from moviebox_api.v2.models import HomepageContentModel, SearchResultsModel


class Homepage(moviebox_api.v1.core.Homepage):
    _url = get_absolute_url('/wefeed-h5api-bff/home?host=moviebox.ph')

    async def get_content_model(self) -> HomepageContentModel:
        """Modelled version of the contents"""
        content = await self.get_content()
        return HomepageContentModel(**content)


class SearchSuggestion(moviebox_api.v1.core.SearchSuggestion):
    _url = get_absolute_url("/wefeed-h5api-bff/subject/search-suggest")


class Search(moviebox_api.v1.core.Search):
    _url = get_absolute_url("/wefeed-h5api-bff/subject/search")

    async def get_content_model(self):
        """Modelled version of the contents.

        Returns:
            SearchResultsModel: Modelled contents
        """
        contents = await self.get_content()
        return SearchResultsModel(**contents)


