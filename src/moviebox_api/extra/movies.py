"""Extra functionalities for movies"""

import warnings
import typing as t
from pathlib import Path
from httpx import Response
from moviebox_api.requests import Session
from moviebox_api.core import Search
from moviebox_api.download import (
    DownloadableMovieFilesDetail,
    MediaFileDownloader,
    CaptionFileDownloader,
    resolve_media_file_to_be_downloaded,
)
from moviebox_api.constants import (
    downloadQualitiesType,
    SubjectType,
    DOWNLOAD_QUALITIES,
    DEFAULT_CAPTION_LANGUAGE,
)
from moviebox_api.helpers import assert_membership
from moviebox_api.models import DownloadableFilesMetadata, SearchResultsItem
from moviebox_api.exceptions import ZeroSearchResultsError

__all__ = ["Auto"]


class Auto:
    """Search movie based on a given query
    and proceed downloading the first one in the results.
    This is a workaround for writing many lines of code
    at the expense of flow control.
    """

    def __init__(
        self,
        session: Session = Session(),
        caption_language: str = DEFAULT_CAPTION_LANGUAGE,
    ):
        """Constructor for `Auto`

        Args:
            session (Session, optional): MovieboxAPI requests session. Defaults to Session().
            caption_language (str, optional): Caption language filter. Defaults to DEFAULT_CAPTION_LANGUAGE.
        """
        self._session = session
        self._caption_language = caption_language

    async def _search_handler(
        self, query: str, year: int | None
    ) -> t.Tuple[SearchResultsItem, DownloadableFilesMetadata]:
        """Performs actual search and get downloadable files metadata.

        Args:
            query (str): Partial or complete movie title.
            year (int, optional): Year filter for the search results to proceed with. Defaults to None.

        Kwargs : Keyworded arguments for `MediaFileDownloader.run` method.

        Returns:
            t.Tuple[SearchResultsItem, DownloadableFilesMetadata].
        """
        search = Search(
            self._session, keyword=query, subject_type=SubjectType.MOVIES, per_page=1
        )
        search_results = await search.get_modelled_content()
        if year is not None:
            target_movie = None
            for item in search_results.items:
                if item.releaseDate.year == year:
                    target_movie = item
                    break
            if target_movie is None:
                raise ZeroSearchResultsError(
                    f"No movie in the search results matched the year filter - {year}. "
                    "Try a different year filter or ommit the filter completely."
                )
        target_movie = search_results.first_item
        downloadable_movie_file_details_inst = DownloadableMovieFilesDetail(
            self._session, target_movie
        )
        downloadable_movie_file_details = (
            await downloadable_movie_file_details_inst.get_modelled_content()
        )
        return target_movie, downloadable_movie_file_details

    async def _movie_download_handler(
        self,
        downloadable_movie_file_details: DownloadableFilesMetadata,
        quality: downloadQualitiesType = "BEST",
        **kwargs,
    ) -> Path | Response:
        """Downloads movie

        Args:
            query (str): Partial or complete movie title.

        Kwargs : Keyworded arguments for `MediaFileDownloader.run` method.

        Returns:
            Path : Downloaded movie file location.
            Response : if test=true
        """
        assert_membership(quality, DOWNLOAD_QUALITIES, "quality")
        target_media_file = resolve_media_file_to_be_downloaded(
            quality, downloadable_movie_file_details
        )
        downloader = MediaFileDownloader(target_media_file)
        saved_to_or_response = await downloader.run(**kwargs)
        return saved_to_or_response

    async def _caption_download_handler(
        self,
        downloadable_movie_file_details: DownloadableFilesMetadata,
        caption_language: str,
        **kwargs,
    ) -> Path | Response:
        """Download caption file.

        Args:
            downloadable_movie_file_details (DownloadableFilesMetadata): Primarily served from `self._search_handler`

        Returns:
            Path: Location under which caption file is saved.
            Response : if test=true
        """

        target_subtitle = downloadable_movie_file_details.get_subtitle_by_language(
            caption_language
        )
        downloader = CaptionFileDownloader(target_subtitle)
        if target_subtitle:
            saved_to_or_response = await downloader.run(**kwargs)
            return saved_to_or_response
        else:
            raise ValueError(
                f"No caption file matched that language - {caption_language}"
            )

    async def run(
        self,
        query: str,
        year: int = None,
        quality: downloadQualitiesType = "BEST",
        caption_language: str = None,
        caption_only: bool = False,
        **kwargs,
    ) -> t.Tuple[Path | Response | None, Path | Response | None]:
        """Perform movie search and download first item in the search results.

        Args:
            query (str): Partial or complete movie title.
            year (int, optional): Year filter for the search results to proceed with. Defaults to None.
            quality (str, optional): Movie quality to download. Defaults to "Best".
            caption_language (str, optional): Overrides caption_language set at class level. Defaults to None.
            caption_only (bool, optional): Download only the caption file and ignore the movie file. Defaults to False.

        Kwargs : Keyworded arguments for `MediaFileDownloader.run` method.

        Returns:
            t.Tuple[Path|Response|None, Path |Response| None]: Path to downloaded movie or httpx response
             and caption file or httpx response respectively.

        """

        target_movie, downloadable_movie_file_details = await self._search_handler(
            query, year
        )
        kwargs.setdefault(
            "filename", target_movie
        )  # SearchResultsItem - auto-filename generation
        caption_language = caption_language or self._caption_language
        movie_saved_to = caption_saved_to = None
        if caption_only:
            if not caption_language:
                warnings.warn(
                    "You have specified to download captions only yet "
                    "you haven't declared the caption_language. "
                    f"Defaulting to caption language - {DEFAULT_CAPTION_LANGUAGE}"
                )
                caption_language = DEFAULT_CAPTION_LANGUAGE
            caption_saved_to = await self._caption_download_handler(
                downloadable_movie_file_details, caption_language, **kwargs
            )
        else:
            # Download subtitle first
            if caption_language:
                caption_saved_to = await self._caption_download_handler(
                    downloadable_movie_file_details, caption_language, **kwargs
                )
            movie_saved_to = await self._movie_download_handler(
                downloadable_movie_file_details, quality, **kwargs
            )
        return (movie_saved_to, caption_saved_to)
