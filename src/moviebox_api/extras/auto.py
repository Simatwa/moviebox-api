"""Extra functionalities for movies"""

import warnings

import httpx
from throttlebuster import DownloadedFile

from moviebox_api.constants import (
    CURRENT_WORKING_DIR,
    DEFAULT_CAPTION_LANGUAGE,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_TASKS,
    DOWNLOAD_PART_EXTENSION,
    DOWNLOAD_QUALITIES,
    DownloadQualitiesType,
    SubjectType,
)
from moviebox_api.core import Search
from moviebox_api.download import (
    CaptionFileDownloader,
    DownloadableMovieFilesDetail,
    MediaFileDownloader,
    resolve_media_file_to_be_downloaded,
)
from moviebox_api.exceptions import ZeroSearchResultsError
from moviebox_api.helpers import assert_membership, get_event_loop
from moviebox_api.models import (
    DownloadableFilesMetadata,
    SearchResultsItem,
)
from moviebox_api.requests import Session

__all__ = ["MovieAuto"]


class MovieAuto:
    """Search movie based on a given query and proceed to download the first one in the results.

    This is a workaround for writing many lines of code at the expense of flow control.
    """

    def __init__(
        self,
        session: Session = None,
        caption_language: str = DEFAULT_CAPTION_LANGUAGE,
        dir: DownloadedFile | str = CURRENT_WORKING_DIR,
        caption_dir: DownloadedFile | str = CURRENT_WORKING_DIR,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        tasks: int = DEFAULT_TASKS,
        part_dir: DownloadedFile | str = CURRENT_WORKING_DIR,
        part_extension: str = DOWNLOAD_PART_EXTENSION,
        merge_buffer_size: int | None = None,
        **httpx_kwargs,
    ):
        """Constructor for `MovieAuto`

        Args:
            session (Session, optional): MovieboxAPI requests session. Defaults to Session().
            caption_language (str, optional): Caption language filter. Defaults to DEFAULT_CAPTION_LANGUAGE.
            dir (DownloadedFile | str, optional): Directory for saving downloaded media files to. Defaults to CURRENT_WORKING_DIR.
            caption_dir (DownloadedFile | str, optional): Directory for saving caption files to. Defaults to CURRENT_WORKING_DIR.
            chunk_size (int, optional): Streaming download chunk size in kilobytes. Defaults to DEFAULT_CHUNK_SIZE.
            tasks (int, optional): Number of tasks to carry out the download. Defaults to DEFAULT_TASKS.
            part_dir (DownloadedFile | str, optional): Directory for temporarily saving downloaded file-parts to. Defaults to CURRENT_WORKING_DIR.
            part_extension (str, optional): Filename extension for download parts. Defaults to DOWNLOAD_PART_EXTENSION.
            merge_buffer_size (int|None, optional). Buffer size for merging the separated files in kilobytes. Defaults to chunk_size.

         httpx_kwargs : Keyword arguments for `httpx.AsyncClient`
        """  # noqa: E501

        self._session = session if session else Session()
        self._caption_language = caption_language

        self.media_file_downloader = MediaFileDownloader(
            dir=dir,
            chunk_size=chunk_size,
            tasks=tasks,
            part_dir=part_dir,
            part_extension=part_extension,
            merge_buffer_size=merge_buffer_size,
            **httpx_kwargs,
        )

        self.caption_file_downloader = CaptionFileDownloader(dir=caption_dir, chunk_size=chunk_size)

    async def _search_handler(
        self, query: str, year: int | None
    ) -> tuple[SearchResultsItem, DownloadableFilesMetadata]:
        """Performs actual search and get downloadable files metadata.

        Args:
            query (str): Partial or complete movie title.
            year (int, optional): Year filter for the search results to proceed with. Defaults to None.

        Kwargs : Keyworded arguments for `MediaFileDownloader.run` method.

        Returns:
            tuple[SearchResultsItem, DownloadableFilesMetadata].
        """
        search = Search(
            self._session,
            query=query,
            subject_type=SubjectType.MOVIES,
            per_page=30,
        )

        search_results = await search.get_content_model()

        if year is not None:
            target_movie = None

            for item in search_results.items:
                if item.releaseDate.year == year:
                    target_movie = item
                    break

            if target_movie is None:
                raise ZeroSearchResultsError(
                    f"No movie in the search results matched the year filter - {year}. "
                    "Try a different value or ommit the filter."
                )

        target_movie = search_results.first_item
        downloadable_movie_file_details_inst = DownloadableMovieFilesDetail(self._session, target_movie)

        downloadable_movie_file_details = await downloadable_movie_file_details_inst.get_content_model()

        return target_movie, downloadable_movie_file_details

    async def _movie_download_handler(
        self,
        downloadable_movie_file_details: DownloadableFilesMetadata,
        quality: DownloadQualitiesType = "BEST",
        **run_kwargs,
    ) -> DownloadedFile | httpx.Response:
        """Downloads movie

        Args:
            downloadable_movie_file_details (DownloadableFilesMetadata): Primarily served from `self._search_handler`.
            quality: Video resolution postpixed with 'P' or simple 'BEST' | 'WORST'. Defaults to 'BEST'

        run_kwargs : Keyword arguments for `MediaFileDownloader.run` method.

        Returns:
            DownloadedFile : Downloaded movie file location.
            httpx.Response : if test=true
        """  # noqa: E501
        assert_membership(quality, DOWNLOAD_QUALITIES, "quality")

        target_media_file = resolve_media_file_to_be_downloaded(quality, downloadable_movie_file_details)

        saved_to_or_response = await self.media_file_downloader.run(target_media_file, **run_kwargs)

        return saved_to_or_response

    async def _caption_download_handler(
        self,
        downloadable_movie_file_details: DownloadableFilesMetadata,
        caption_language: str,
        **run_kwargs,
    ) -> DownloadedFile | httpx.Response:
        """Download caption file.

        Args:
            downloadable_movie_file_details (DownloadableFilesMetadata): Primarily served from `self._search_handler`.
            caption_language: Subtitle language e.g 'English' or simply 'en'.

        run_kwargs : Keyword arguments for `CaptionFileDownloader.run` method.

        Returns:
            DownloadedFile: Location under which caption file is saved.
            httpx.Response : if test=true
        """  # noqa: E501

        target_subtitle = downloadable_movie_file_details.get_subtitle_by_language(caption_language)

        if target_subtitle:
            saved_to_or_response = await self.caption_file_downloader.run(target_subtitle, **run_kwargs)

            return saved_to_or_response

        else:
            raise ValueError(f"No caption file matched that language - {caption_language}")

    async def run(
        self,
        query: str,
        year: int = None,
        quality: DownloadQualitiesType = "BEST",
        caption_language: str = None,
        caption_only: bool = False,
        **kwargs,
    ) -> tuple[DownloadedFile | httpx.Response | None, DownloadedFile | httpx.Response | None]:
        """Perform movie search and download first item in the search results.

        Args:
            query (str): Partial or complete movie title.
            year (int, optional): Year filter for the search results to proceed with. Defaults to None.
            quality (str, optional): Movie quality to download. Defaults to "Best".
            caption_language (str, optional): Overrides caption_language set at class level. Defaults to None.
            caption_only (bool, optional): Download only the caption file and ignore the movie file. Defaults to False.

        Kwargs : Keyworded arguments for `MediaFileDownloader.run` method.

        Returns:
            tuple[DownloadedFile|httpx.Response|None, DownloadedFile |httpx.Response| None]: Downloaded movie details or httpx response
             and caption file or httpx response respectively.

        """  # noqa: E501

        (
            target_movie,
            downloadable_movie_file_details,
        ) = await self._search_handler(query, year)

        kwargs.setdefault("filename", target_movie)  # SearchResultsItem - auto-filename generation

        caption_language = caption_language or self._caption_language
        movie_details_or_httpx_response = caption_details_or_httpx_response = None

        if caption_only:
            if not caption_language:
                warnings.warn(
                    "You have specified to download captions only yet "
                    "you haven't declared the caption_language. "
                    f"Defaulting to caption language - {DEFAULT_CAPTION_LANGUAGE}"
                )
                caption_language = DEFAULT_CAPTION_LANGUAGE

            caption_details_or_httpx_response = await self._caption_download_handler(
                downloadable_movie_file_details,
                caption_language,
                **kwargs,
            )

        else:
            # Download subtitle first
            if caption_language:
                caption_details_or_httpx_response = await self._caption_download_handler(
                    downloadable_movie_file_details,
                    caption_language,
                    **kwargs,
                )

            movie_details_or_httpx_response = await self._movie_download_handler(
                downloadable_movie_file_details, quality, **kwargs
            )

        return (movie_details_or_httpx_response, caption_details_or_httpx_response)

    def run_sync(
        self, *args, **kwargs
    ) -> tuple[DownloadedFile | httpx.Response | None, DownloadedFile | httpx.Response | None]:
        """Synchronously perform movie search and download first item in the search results."""
        return get_event_loop().run_until_complete(self.run(*args, **kwargs))


class TVSeriesAuto:
    pass
