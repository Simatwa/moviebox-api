"""Stream media file. Optimized for real time display."""

from typing import Dict
from moviebox_api._bases import BaseContentProvider
from moviebox_api.models import SearchResultsItem, StreamFilesMetadata
from moviebox_api.requests import Session
from moviebox_api.helpers import (
    assert_instance,
    get_absolute_url,
)


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

    def _create_request_params(self) -> Dict:
        """Creates request parameters
        Returns:
            Dict: Request params
        """
        # se -> season
        # ep -> episode
        return {"subjectId": self._item.subjectId, "se": 1, "ep": 1}

    async def get_content(self) -> Dict:
        """Performs the actual fetching of files detail.

        Returns:
            Dict: File details
        """
        # Referer
        request_header = {
            "Referer": get_absolute_url(f"/movies/{self._item.detailPath}")
        }
        # Without the referer, empty response will be served.

        content = await self.session.get_with_cookies_from_api(
            url=self._url,
            params=self._create_request_params(),
            headers=request_header,
        )
        return content

    async def get_modelled_content(self) -> StreamFilesMetadata:
        """Get modelled version of the streamable files detail.

        Returns:
            StreamFilesMetadata: Modelled file details
        """
        contents = await self.get_content()
        return StreamFilesMetadata(**contents)
