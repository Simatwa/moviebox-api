import typing as t

from moviebox_api.v1._bases import BaseContentProviderAndHelper
from moviebox_api.v1.helpers import assert_instance
from moviebox_api.v2.exceptions import InvalidDetailPathError
from moviebox_api.v2.helpers import get_absolute_url, validate_detail_path
from moviebox_api.v2.models import SpecificItemDetailsModel
from moviebox_api.v2.requests import Session


class BaseItemDetails(BaseContentProviderAndHelper):
    """Base class for specific movie/tv-series (item) details"""

    api_endpoint = get_absolute_url("/wefeed-h5api-bff/detail")

    def __init__(self, session: Session):
        """Constructor for `BaseItemDetails`

        Args:
            detail_path (str): Specific item detail path
            session (Session): MovieboxAPI request session
        """
        assert_instance(session, Session, "session")
        self._session = session

    def _validate_detail_path(self, detail_path: str) -> t.NoReturn:
        if not validate_detail_path(detail_path):
            raise InvalidDetailPathError(
                f"Invalid detail path passed {detail_path!r} "
                "Recheck and try again"
            )

    async def get_content(self, detail_path: str) -> dict:
        self._validate_detail_path(detail_path)
        content = await self._session.get_from_api(
            self.api_endpoint, params={"detailPath": detail_path}
        )
        return content

    async def get_content_model(
        self, detail_path: str, **kwargs
    ) -> SpecificItemDetailsModel:

        content = await self.get_content(detail_path, **kwargs)
        modelled_content = SpecificItemDetailsModel(**content)

        return modelled_content
