"""Stream media file. Optimized for real time display."""

# TODO: Write unittest for this module

from moviebox_api._bases import BaseContentProvider
from moviebox_api.helpers import (
    assert_instance,
    get_absolute_url,
)
from moviebox_api.models import SearchResultsItem, StreamFilesMetadata
from moviebox_api.requests import Session


class StreamFilesDetail(BaseContentProvider):
    # https://moviebox.ng/wefeed-h5-bff/web/subject/play?subjectId=4006958073083480920&se=1&ep=1
    _url = get_absolute_url(r"/wefeed-h5-bff/web/subject/play")

    def __init__(self, session: Session, item: SearchResultsItem):
        """Constructor for `StreamFilesDetail`

        Args:
            session (Session): MovieboxAPI request session.
            item (SearchResultsItem): Movie item to handle.
        """
        assert_instance(session, Session, "session")
        assert_instance(item, SearchResultsItem, "item")
        self.session = session
        self._item = item

    def _create_request_params(self, season: int, episode: int) -> dict:
        """Creates request parameters

        Args:
            season (int): Season number of the target item.
            episde (int): Episode number of the target item.
        Returns:
            dict: Request params
        """
        return {
            "subjectId": self._item.subjectId,
            "se": season,
            "ep": episode,
        }

    async def get_content(self, season: int, episode: int) -> dict:
        """Performs the actual fetching of files detail.

        Args:
            season (int): Season number of the target item.
            episde (int): Episode number of the target item.

        Returns:
            dict: File details
        """
        # Referer
        request_header = {"Referer": get_absolute_url(f"/movies/{self._item.detailPath}")}
        # Without the referer, empty response will be served.

        content = await self.session.get_with_cookies_from_api(
            url=self._url,
            params=self._create_request_params(season, episode),
            headers=request_header,
        )
        return content

    async def get_modelled_content(self, season: int, episode: int) -> StreamFilesMetadata:
        """Get modelled version of the streamable files detail.

        Args:
            season (int): Season number of the target item.
            episde (int): Episode number of the target item

        Returns:
            StreamFilesMetadata: Modelled stream files details
        """
        contents = await self.get_content(season, episode)
        return StreamFilesMetadata(**contents)
