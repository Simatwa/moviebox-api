import typing as t

from moviebox_api.v1._bases import BaseContentProviderAndHelper
from moviebox_api.v1.requests import Session
from moviebox_api.v2.models import SearchResultsItem


class BaseSearch(BaseContentProviderAndHelper):
    """Base class for search providers such as `Trending` and `Search`"""

    session: Session
    """Moviebox-api requests session"""

    _url: str

    def _create_payload(self) -> dict[str, t.Any]:
        raise NotImplementedError("Function needs to be implemented in subclass")

    async def get_content(self) -> dict:
        """Fetches content

        Returns:
            dict: Fetched results
        """
        contents = await self.session.get_from_api(url=self._url, params=self._create_payload())
        return contents

    def get_item_details(self, item: SearchResultsItem) -> "MovieDetails | TVSeriesDetails":
        """Get object that provide more details about the search results item such as casts, seasons etc

        Args:
            item (SearchResultsItem): Search result item

        Returns:
            MovieDetails | TVSeriesDetails: Object providing more details about the item
        """
        # TODO: Implement this later
        assert_instance(item, SearchResultsItem, "item")
        match item.subjectType:
            case SubjectType.MOVIES:
                return MovieDetails(item, self.session)
            case SubjectType.TV_SERIES:
                return TVSeriesDetails(item, self.session)
            case _:
                raise NotImplementedError(
                    f"Currently only items of {SubjectType.MOVIES.name} and {SubjectType.TV_SERIES.name} "
                    "subject-types are supported. Check later versions for possible support of other "
                    "subject-types"
                )