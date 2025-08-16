"""Gets the work done - downloads media with flexible flow control"""

import asyncio
from pathlib import Path

import httpx
from throttlebuster import DownloadedFile
from throttlebuster.constants import DOWNLOAD_PART_EXTENSION

from moviebox_api.cli.helpers import (
    get_caption_file_or_raise,
    perform_search_and_get_item,
)
from moviebox_api.constants import (
    CURRENT_WORKING_DIR,
    DEFAULT_CAPTION_LANGUAGE,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_TASKS,
    DOWNLOAD_QUALITIES,
    DownloadQualitiesType,
    SubjectType,
)
from moviebox_api.core import Session
from moviebox_api.download import (
    CaptionFileDownloader,
    DownloadableMovieFilesDetail,
    DownloadableTVSeriesFilesDetail,
    MediaFileDownloader,
    resolve_media_file_to_be_downloaded,
)
from moviebox_api.helpers import assert_instance, assert_membership
from moviebox_api.models import SearchResultsItem

__all__ = ["Downloader"]


class Downloader:
    """Controls the movie/series download process"""

    def __init__(self, session: Session = Session()):
        """Constructor for `Downloader`

        Args:
            session (Session, optional): MovieboxAPI httpx request session . Defaults to Session().
        """
        assert_instance(session, Session, "session")
        self._session = session

    async def download_movie(
        self,
        title: str,
        year: int | None = None,
        yes: bool = False,
        dir: Path | str = CURRENT_WORKING_DIR,
        caption_dir: Path | str = CURRENT_WORKING_DIR,
        quality: DownloadQualitiesType = "BEST",
        movie_filename_tmpl: str = MediaFileDownloader.movie_filename_template,
        caption_filename_tmpl: str = CaptionFileDownloader.movie_filename_template,
        language: tuple[str] = (DEFAULT_CAPTION_LANGUAGE,),
        download_caption: bool = False,
        caption_only: bool = False,
        search_function: callable = perform_search_and_get_item,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        tasks: int = DEFAULT_TASKS,
        part_dir: Path | str = CURRENT_WORKING_DIR,
        part_extension: str = DOWNLOAD_PART_EXTENSION,
        merge_buffer_size: int | None = None,
        **run_kwargs,
    ) -> tuple[
        DownloadedFile | httpx.Response | None,
        list[DownloadedFile | httpx.Response] | None,
    ]:
        """Search movie by name and proceed to download it.

        Args:
            title (str): Complete or partial movie name
            year (int|None, optional): `releaseDate.year` filter for the movie. Defaults to None.
            yes (bool, optional): Proceed with the first item in the results instead of prompting confirmation. Defaults to False
            dir (Path|str, optional): Directory for saving the movie file to. Defaults to CURRENT_WORKING_DIR.
            caption_dir (Path|str, optional): Directory for saving the caption file to. Defaults to CURRENT_WORKING_DIR.
            quality (DownloadQualitiesType, optional): Such as `720p` or simply `BEST` etc. Defaults to 'BEST'.
            movie_filename_tmpl (str, optional): Template for generating movie filename. Defaults to MediaFileDownloader.movie_filename_template.
            caption_filename_tmpl (str, optional): Template for generating caption filename. Defaults to CaptionFileDownloader.movie_filename_template.
            language (tuple, optional): Languages to download captions in. Defaults to (DEFAULT_CAPTION_LANGUAGE,).
            download_caption (bool, optional): Whether to download caption or not. Defaults to False.
            caption_only (bool, optional): Whether to ignore movie file or not. Defaults to False.
            search_function (callable, optional): Accepts `session`, `title`, `year`, `subject_type` & `yes` and returns `SearchResultsItem`.
            chunk_size (int, optional): Streaming download chunk size in kilobytes. Defaults to DEFAULT_CHUNK_SIZE.
            tasks (int, optional): Number of tasks to carry out the download. Defaults to DEFAULT_TASKS.
            part_dir (Path | str, optional): Directory for temporarily saving the downloaded file-parts to. Defaults to CURRENT_WORKING_DIR.
            part_extension (str, optional): Filename extension for download parts. Defaults to DOWNLOAD_PART_EXTENSION.
            merge_buffer_size (int|None, optional). Buffer size for merging the separated files in kilobytes. Defaults to chunk_size.

        run_kwargs: Other keyword arguments for `MediaFileDownloader.run`

        Returns:
            tuple[DownloadedFile | httpx.Response  | None, list[DownloadedFile | httpx.Response ] | None]: Path to downloaded movie and downloaded caption files.
        """  # noqa: E501

        assert_membership(quality, DOWNLOAD_QUALITIES)

        assert callable(search_function), (
            f"Value for search_function must be callable not {type(search_function)}"
        )

        MediaFileDownloader.movie_filename_template = movie_filename_tmpl
        CaptionFileDownloader.movie_filename_template = caption_filename_tmpl

        target_movie = await search_function(
            self._session,
            title=title,
            year=year,
            subject_type=SubjectType.MOVIES,
            yes=yes,
        )

        assert isinstance(target_movie, SearchResultsItem), (
            f"Search function {search_function.__name__} must return an instance of "
            f"{SearchResultsItem} not {type(target_movie)}"
        )

        downloadable_details_inst = DownloadableMovieFilesDetail(self._session, target_movie)

        downloadable_details = await downloadable_details_inst.get_content_model()

        target_media_file = resolve_media_file_to_be_downloaded(quality, downloadable_details)

        subtitle_details_items = []

        if download_caption or caption_only:
            for lang in language:
                target_caption_file = get_caption_file_or_raise(downloadable_details, lang)
                caption_downloader = CaptionFileDownloader(
                    dir=caption_dir,
                    chunk_size=chunk_size,
                    tasks=tasks,
                    part_dir=part_dir,
                    part_extension=part_extension,
                    merge_buffer_size=merge_buffer_size,
                )

                subtitle_details = await caption_downloader.run(
                    caption_file=target_caption_file,
                    filename=target_movie,
                    **run_kwargs,
                )

                subtitle_details_items.append(subtitle_details)

            if caption_only:
                # terminate
                return (None, subtitle_details_items)

        movie_downloader = MediaFileDownloader(
            dir=dir,
            chunk_size=chunk_size,
            tasks=tasks,
            part_dir=part_dir,
            part_extension=part_extension,
            merge_buffer_size=merge_buffer_size,
        )

        movie_details = await movie_downloader.run(
            media_file=target_media_file, filename=target_movie, **run_kwargs
        )
        return (movie_details, subtitle_details_items)

    async def download_tv_series(
        self,
        title: str,
        season: int,
        episode: int,
        year: int | None = False,
        yes: bool = False,
        dir: Path | str = CURRENT_WORKING_DIR,
        caption_dir: Path | str = CURRENT_WORKING_DIR,
        quality: DownloadQualitiesType = "BEST",
        episode_filename_tmpl: str = MediaFileDownloader.series_filename_template,
        caption_filename_tmpl: str = CaptionFileDownloader.series_filename_template,
        language: tuple = (DEFAULT_CAPTION_LANGUAGE,),
        download_caption: bool = False,
        caption_only: bool = False,
        limit: int = 1,
        search_function: callable = perform_search_and_get_item,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        tasks: int = DEFAULT_TASKS,
        part_dir: Path | str = CURRENT_WORKING_DIR,
        part_extension: str = DOWNLOAD_PART_EXTENSION,
        merge_buffer_size: int | None = None,
        **run_kwargs,
    ) -> dict[
        int,
        dict[str, DownloadedFile | httpx.Response | list[DownloadedFile | httpx.Response]],
    ]:
        """Search tv-series by name and proceed to download its episodes.

        Args:
            title (str): Complete or partial tv-series name.
            season (int): Target season number of the tv-series.
            episode (int): Target episode number of the tv-series.
            year (int|None, optional): `releaseDate.year` filter for the tv-series. Defaults to None.
            yes (bool, optional): Proceed with the first item in the results instead of prompting confirmation. Defaults to False.
            dir (Path|str, optional): Directory for saving the movie file to. Defaults to CURRENT_WORKING_DIR.
            caption_dir (Path|str, optional): Directory for saving the caption files to. Defaults to CURRENT_WORKING_DIR.
            quality (DownloadQualitiesType, optional): Episode quality such as `720p` or simply `BEST` etc. Defaults to 'BEST'.
            episode_filename_tmpl (str, optional): Template for generating episode filename. Defaults to MediaFileDownloader.series_filename_template.
            caption_filename_tmpl (str, optional): Template for generating caption filename. Defaults to CaptionFileDownloader.series_filename_template.
            language (tuple, optional): Languages to download captions in. Defaults to (DEFAULT_CAPTION_LANGUAGE,).
            download_caption (bool, optional): Whether to download caption or not. Defaults to False.
            caption_only (bool, optional): Whether to ignore episode files or not. Defaults to False.
            limit (int, optional): Number of episodes to download including the offset episode. Defaults to 1.
            search_function (callable, optional): Accepts `session`, `title`, `year`, `subject_type` & `yes` and returns item.
            chunk_size (int, optional): Streaming download chunk size in kilobytes. Defaults to DEFAULT_CHUNK_SIZE.
            tasks (int, optional): Number of tasks to carry out the download. Defaults to DEFAULT_TASKS.
            part_dir (Path | str, optional): Directory for temporarily saving the downloaded file-parts to. Defaults to CURRENT_WORKING_DIR.
            part_extension (str, optional): Filename extension for download parts. Defaults to DOWNLOAD_PART_EXTENSION.
            merge_buffer_size (int|None, optional). Buffer size for merging the separated files in kilobytes. Defaults to chunk_size.

        run_kwargs: Other keyword arguments for `MediaFileDownloader.run`

        Returns:
             dict[int, dict[str, DownloadedFile | httpx.Response  | list[DownloadedFile | httpx.Response ]]]: Episode number and downloaded episode file details and caption files.
        """  # noqa: E501

        assert_membership(quality, DOWNLOAD_QUALITIES)

        assert callable(search_function), (
            f"Value for search_function must be callable not {type(search_function)}"
        )

        MediaFileDownloader.series_filename_template = episode_filename_tmpl
        CaptionFileDownloader.series_filename_template = caption_filename_tmpl

        target_tv_series = await search_function(
            self._session,
            title=title,
            year=year,
            subject_type=SubjectType.TV_SERIES,
            yes=yes,
        )
        assert isinstance(target_tv_series, SearchResultsItem), (
            f"Search function {search_function.__name__} must return an instance of "
            f"{SearchResultsItem} not {type(target_tv_series)}"
        )

        downloadable_files = DownloadableTVSeriesFilesDetail(self._session, target_tv_series)
        response = {}

        caption_downloader = CaptionFileDownloader(
            dir=caption_dir,
            chunk_size=chunk_size,
            tasks=tasks,
            part_dir=part_dir,
            part_extension=part_extension,
            merge_buffer_size=merge_buffer_size,
        )

        media_file_downloader = MediaFileDownloader(
            dir=dir,
            chunk_size=chunk_size,
            tasks=tasks,
            part_dir=part_dir,
            part_extension=part_extension,
            merge_buffer_size=merge_buffer_size,
        )

        for episode_count in range(limit):
            current_episode = episode + episode_count

            downloadable_files_detail = await downloadable_files.get_content_model(
                season=season, episode=current_episode
            )

            # TODO: Iterate over seasons as well
            # - With regard to season details

            current_episode_details = {}
            caption_details_items = []

            if caption_only or download_caption:
                for lang in language:
                    target_caption_file = get_caption_file_or_raise(downloadable_files_detail, lang)

                    caption_filename = caption_downloader.generate_filename(
                        target_tv_series,
                        caption_file=target_caption_file,
                        season=season,
                        episode=current_episode,
                    )

                    caption_details = await caption_downloader.run(
                        caption_file=target_caption_file,
                        filename=caption_filename,
                        **run_kwargs,
                    )

                    caption_details_items.append(caption_details)

                if caption_only:
                    # Avoid downloading tv-series
                    continue

            # Download series

            current_episode_details["captions"] = caption_details_items

            target_media_file = resolve_media_file_to_be_downloaded(quality, downloadable_files_detail)

            filename = media_file_downloader.generate_filename(
                target_tv_series,
                media_file=target_media_file,
                season=season,
                episode=current_episode,
            )

            tv_series_details = await media_file_downloader.run(
                media_file=target_media_file, filename=filename, **run_kwargs
            )

            current_episode_details["movie"] = tv_series_details
            response[current_episode] = current_episode_details

        return response

    def download_movie_sync(
        self,
        *args,
        **kwargs,
    ) -> tuple[
        DownloadedFile | httpx.Response | None,
        list[DownloadedFile | httpx.Response] | None,
    ]:
        """Synchronously search movie by name and proceed to download it."""
        return asyncio.get_event_loop().run_until_complete(self.download_movie(*args, **kwargs))

    def download_tv_series_sync(
        self,
        *args,
        **kwargs,
    ) -> dict[
        int,
        dict[str, DownloadedFile | httpx.Response | list[DownloadedFile | httpx.Response]],
    ]:
        """Synchronously search tv-series by name and proceed to download its episodes."""
        return asyncio.get_event_loop().run_until_complete(self.download_tv_series(*args, **kwargs))
