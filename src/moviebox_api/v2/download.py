"""For finding downloadable media files
and initiating actual download
"""

from abc import ABCMeta

from moviebox_api.v1._bases import BaseContentProviderAndHelper
from moviebox_api.v1.download import CaptionFileDownloader, MediaFileDownloader
from moviebox_api.v1.helpers import assert_instance
from moviebox_api.v1.models import DownloadableFilesMetadata
from moviebox_api.v2.constants import SubjectType
from moviebox_api.v2.helpers import get_absolute_url
from moviebox_api.v2.models import SearchResultsItem
from moviebox_api.v2.requests import Session

__all__ = [
    "CaptionFileDownloader",
    "MediaFileDownloader",
    "DownloadableSingleFilesDetail",
    "DownloadableMovieFilesDetail",
    "DownloadableMusicFilesDetail",
    "DownloadableAnimeFilesDetail",
    "DownloadableEducationFilesDetail",
    "DownloadableTVSeriesFilesDetail",
]


class ImmutableMeta(ABCMeta):
    def __setattr__(cls, name, value):
        if name == "_subject_types":
            raise AttributeError("_subject_types is immutable")

        super().__setattr__(name, value)


class BaseDownloadableFilesDetail(
    BaseContentProviderAndHelper, metaclass=ImmutableMeta
):
    """Base class for fetching and modelling downloadable files detail"""

    _url = get_absolute_url(r"/wefeed-h5api-bff/subject/download")

    _subject_types: tuple[SubjectType] = None
    """Enforce item to be of this subjectType(s). Defaults to None"""

    def __init__(
        self,
        session: Session,
        item: SearchResultsItem,
    ):
        """Constructor for `BaseDownloadableFilesDetail`

        Args:
            session (Session): MovieboxAPI request session.
            item (SearchResultsItem): Movie/TVSeries item
                to handle
        """
        assert_instance(session, Session, "session")
        assert_instance(item, SearchResultsItem, "item")

        if self._subject_types is not None:
            if item.subjectType not in self._subject_types:
                raise ValueError(
                    "item needs to be /any/ of the subjectType(s) "
                    f"{self._subject_types!r}",
                    f"not {item.subjectType!r}",
                )

        self.session = session
        self._item = item

    def _create_request_params(self, season: int, episode: int) -> dict:
        """Creates request parameters

        Args:
            season (int): Season number of the series.
            episde (int): Episode number of the series.
        Returns:
            t.Dict: Request params
        """
        return {
            "subjectId": self._item.subjectId,
            "se": season,
            "ep": episode,
            "detailPath": self._item.detailPath,
        }

    async def get_content(self, season: int, episode: int) -> dict:
        """Performs the actual fetching of files detail.

        Args:
            season (int): Season number of the series.
            episde (int): Episode number of the series.

        Returns:
            t.Dict: File details
        """

        content = await self.session.get_from_api(
            url=self._url,
            params=self._create_request_params(season, episode),
        )
        return content

    async def get_content_model(
        self, season: int, episode: int
    ) -> DownloadableFilesMetadata:
        """Get modelled version of the downloadable files detail.

        Args:
            season (int): Season number of the series.
            episde (int): Episode number of the series.

        Returns:
            DownloadableFilesMetadata: Modelled file details
        """
        contents = await self.get_content(season, episode)
        return DownloadableFilesMetadata(**contents)


class DownloadableSingleFilesDetail(BaseDownloadableFilesDetail):
    """Fetches and model movie/music/anime/education files detail"""

    _subject_types = (
        SubjectType.MOVIES,
        SubjectType.ANIME,
        SubjectType.MUSIC,
        SubjectType.EDUCATION,
    )

    async def get_content(self) -> dict:
        """Actual fetch of files detail"""
        return await super().get_content(season=0, episode=0)

    async def get_content_model(self) -> DownloadableFilesMetadata:
        """Modelled version of the files detail"""
        contents = await self.get_content()
        return DownloadableFilesMetadata(**contents)


DownloadableMovieFilesDetail = DownloadableMusicFilesDetail = (
    DownloadableAnimeFilesDetail
) = DownloadableEducationFilesDetail = DownloadableSingleFilesDetail


class DownloadableTVSeriesFilesDetail(BaseDownloadableFilesDetail):
    """Fetches and model tv-series files detail"""

    _subject_types = (SubjectType.TV_SERIES,)

    # NOTE: Already implemented by parent class - BaseDownloadableFilesDetail
