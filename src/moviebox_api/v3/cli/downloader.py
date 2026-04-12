"""Gets the work done - downloads media with flexible flow control

- Supports both API versions - v1, v2
"""

import logging
import tempfile
from pathlib import Path
from typing import Literal

import httpx
from throttlebuster import DownloadedFile
from throttlebuster.constants import DOWNLOAD_PART_EXTENSION

from moviebox_api.v3.cli.helpers import (
    get_caption_file_or_raise,
    media_player_name_func_map,
    perform_search_and_get_item,
)
from moviebox_api.v3.constants import (
    CURRENT_WORKING_DIR,
    DEFAULT_CAPTION_LANGUAGE,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_TASKS,
    CustomResolutionType,
    SubjectType,
)
from moviebox_api.v3.core import DownloadableFilesDetail, SeasonDetails
from moviebox_api.v3.download import (
    CaptionFileDownloader,
    MediaFileDownloader,
    resolve_media_file_to_be_downloaded,
)
from moviebox_api.v3.exceptions import ZeroCaptionFileError
from moviebox_api.v3.helpers import (
    assert_instance,
    get_download_tv_series_request_params,
    get_event_loop,
)
from moviebox_api.v3.http_client import MovieBoxHttpClient
from moviebox_api.v3.models.search import ResultsSubjectModel

__all__ = ["Downloader"]


class Downloader:
    """Controls the movie/series download process"""

    def __init__(
        self,
        client_session: MovieBoxHttpClient,
    ):
        """Constructor for `Downloader`"""
        logging.warning(
            "V3 of moviebox-API lacks subtitles support. All options related to "
            "captions will be ignored. "
            "You can find the report at https://github.com/Simatwa/moviebox-api/issues/85."
        )
        self.client_session = client_session

    def __setattr__(self, name, value):
        match name:
            case "client_session":
                assert_instance(value, MovieBoxHttpClient, "client_session")

        super().__setattr__(name, value)

    async def download_movie(
        self,
        title: str,
        year: int | None = None,
        yes: bool = False,
        dir: Path | str = CURRENT_WORKING_DIR,
        caption_dir: Path | str = CURRENT_WORKING_DIR,
        quality: CustomResolutionType = CustomResolutionType.BEST,
        movie_filename_tmpl: str = MediaFileDownloader.movie_filename_template,
        caption_filename_tmpl: str = CaptionFileDownloader.movie_filename_template,  # noqa: E501
        language: tuple[str] = (DEFAULT_CAPTION_LANGUAGE,),
        download_caption: bool = False,
        caption_only: bool = False,
        stream_via: Literal["mpv", "vlc"] | None = None,
        search_function: callable = perform_search_and_get_item,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        tasks: int = DEFAULT_TASKS,
        part_dir: Path | str = CURRENT_WORKING_DIR,
        part_extension: str = DOWNLOAD_PART_EXTENSION,
        merge_buffer_size: int | None = None,
        ignore_missing_caption: bool = False,
        subject_type: SubjectType = SubjectType.MOVIES,
        **run_kwargs,
    ) -> tuple[
        DownloadedFile | httpx.Response | None,
        list[DownloadedFile | httpx.Response] | None,
    ]:
        """Search movie by name and proceed to download it or stream it.

        Args:
            title (str): Complete or partial movie name

            year (int|None, optional): `releaseDate.year` filter for the movie.
                Defaults to None.

            yes (bool, optional): Proceed with the first item in the results
                instead of prompting confirmation. Defaults to False

            dir (Path|str, optional): Directory for saving the movie file to.
                Defaults to CURRENT_WORKING_DIR.

            caption_dir (Path|str, optional): Directory for saving the caption
                file to. Defaults to CURRENT_WORKING_DIR.

            quality (DownloadQualitiesType, optional): Such as `720p` or simply
                `BEST` etc. Defaults to CustomResolutionType.BEST.

            movie_filename_tmpl (str, optional): Template for generating movie
                filename. Defaults to MediaFileDownloader.movie_filename_template.

            caption_filename_tmpl (str, optional): Template for generating caption
                filename. Defaults to
                CaptionFileDownloader.movie_filename_template.

            language (tuple, optional): Languages to download captions in.
                Defaults to (DEFAULT_CAPTION_LANGUAGE,).

            download_caption (bool, optional): Whether to download caption or not.
                Defaults to False.

            caption_only (bool, optional): Whether to ignore movie file or not.
                Defaults to False.

            stream_via (Literal["mpv", "vlc"] | None = None, optional): Stream
                directly in chosen media_player instead of downloading.
                Defaults to None.

            search_function (callable, optional): Accepts `session`, `title`,
                `year`, `subject_type` & `yes` and returns `ResultsSubjectModel`.

            chunk_size (int, optional): Streaming download chunk size in
                kilobytes. Defaults to DEFAULT_CHUNK_SIZE.

            tasks (int, optional): Number of tasks to carry out the download.
                Defaults to DEFAULT_TASKS.

            part_dir (Path | str, optional): Directory for temporarily saving the
                downloaded file-parts to. Defaults to CURRENT_WORKING_DIR.

            part_extension (str, optional): Filename extension for download parts.
                 Defaults to DOWNLOAD_PART_EXTENSION.

            merge_buffer_size (int|None, optional). Buffer size for merging the
                separated files in kilobytes. Defaults to chunk_size.

        run_kwargs: Other keyword arguments for `MediaFileDownloader.run`

        Returns:
            tuple[DownloadedFile | httpx.Response  | None, list[DownloadedFile |
            httpx.Response ] | None]: Path to downloaded movie and downloaded
              caption files.
        """

        assert_instance(quality, CustomResolutionType, "quality")

        # TODO: remove this when subtitles support will be available
        download_caption = False
        caption_only = False
        language = tuple()

        assert callable(search_function), (
            "Value for search_function must be callable not"
            f"{type(search_function)}"
        )

        MediaFileDownloader.movie_filename_template = movie_filename_tmpl
        CaptionFileDownloader.movie_filename_template = caption_filename_tmpl

        target_movie = await search_function(
            self.client_session,
            title=title,
            year=year,
            subject_type=subject_type,
            yes=yes,
        )

        assert isinstance(target_movie, ResultsSubjectModel), (
            f"Search function {search_function.__name__} must return an instance "
            f"of {ResultsSubjectModel} not {type(target_movie)}"
        )

        downloadable_details_inst = DownloadableFilesDetail(self.client_session)

        downloadable_files_detail = (
            await downloadable_details_inst.get_content_model(
                target_movie.subject_id,
                release_date=str(target_movie.release_date),
            )
        )

        target_media_file = resolve_media_file_to_be_downloaded(
            quality, downloadable_files_detail
        )
        # TODO: feature missing caption file processing implementation for v3

        subtitle_details_items: list[DownloadedFile] = []

        subtitles_dir = tempfile.mkdtemp() if stream_via else caption_dir

        if download_caption or caption_only:
            for lang in language:
                try:
                    target_caption_file = get_caption_file_or_raise(
                        downloadable_files_detail, lang
                    )

                except (ZeroCaptionFileError, ValueError):
                    if ignore_missing_caption:
                        continue
                    raise

                caption_downloader = CaptionFileDownloader(
                    dir=subtitles_dir,
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

            if caption_only and not stream_via:
                # terminate
                return (None, subtitle_details_items)

        if stream_via:
            return media_player_name_func_map[stream_via](
                str(target_media_file.url), subtitle_details_items, subtitles_dir
            )

        movie_downloader = MediaFileDownloader(
            dir=dir,
            chunk_size=chunk_size,
            tasks=tasks,
            part_dir=part_dir,
            part_extension=part_extension,
            merge_buffer_size=merge_buffer_size,
        )

        movie_details = await movie_downloader.run(
            media_file=target_media_file,
            filename=downloadable_files_detail,
            **run_kwargs,
        )
        return (movie_details, subtitle_details_items)

    async def download_tv_series(
        self,
        title: str,
        season: int = 1,
        episode: int = 1,
        year: int | None = None,
        yes: bool = False,
        dir: Path | str = CURRENT_WORKING_DIR,
        caption_dir: Path | str = CURRENT_WORKING_DIR,
        quality: CustomResolutionType = CustomResolutionType.BEST,
        episode_filename_tmpl: str = MediaFileDownloader.series_filename_template,
        caption_filename_tmpl: str = CaptionFileDownloader.series_filename_template,  # noqa: E501
        language: tuple = (DEFAULT_CAPTION_LANGUAGE,),
        download_caption: bool = False,
        caption_only: bool = False,
        stream_via: Literal["mpv", "vlc"] | None = None,
        limit: int = -1,
        search_function: callable = perform_search_and_get_item,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        tasks: int = DEFAULT_TASKS,
        part_dir: Path | str = CURRENT_WORKING_DIR,
        part_extension: str = DOWNLOAD_PART_EXTENSION,
        merge_buffer_size: int | None = None,
        ignore_missing_caption: bool = False,
        auto_mode: bool = False,
        format: Literal["group", "struct"] | None = None,
        **run_kwargs,
    ) -> dict[
        int,
        dict[
            int,
            dict[
                str,
                DownloadedFile
                | httpx.Response
                | list[DownloadedFile | httpx.Response],
            ],
        ],
    ]:
        """Search tv-series by name and proceed to download or stream its
            episodes.

        Args:
            title (str): Complete or partial tv-series name.

            season (int): Target season number of the tv-series to start
                processing from.

            episode (int): Target episode number of the tv-series to start
                processing from.

            year (int|None, optional): `releaseDate.year` filter for the
                tv-series. Defaults to None.

            yes (bool, optional): Proceed with the first item in the results
                instead of prompting confirmation. Defaults to False.

            dir (Path|str, optional): Directory for saving the movie file to.
                Defaults to CURRENT_WORKING_DIR.

            caption_dir (Path|str, optional): Directory for saving the caption
                files to. Defaults to CURRENT_WORKING_DIR.

            quality (DownloadQualitiesType, optional): Episode quality such as
                `720p` or simply `BEST` etc. Defaults to
                CustomResolutionType.BEST.

            episode_filename_tmpl (str, optional): Template for generating episode
                filename. Defaults to
                MediaFileDownloader.series_filename_template.

            caption_filename_tmpl (str, optional): Template for generating
                caption filename. Defaults to
                CaptionFileDownloader.series_filename_template.

            language (tuple, optional): Languages to download captions in.
                Defaults to (DEFAULT_CAPTION_LANGUAGE,).

            download_caption (bool, optional): Whether to download caption or not.
                Defaults to False.

            caption_only (bool, optional): Whether to ignore episode files or not.
                Defaults to False.

            stream_via (Literal["mpv", "vlc"], optional): Stream directly in
                chosen media played instead of downloading. Defaults to None.

            limit (int, optional): Number of episodes to download including the
                offset episode. Defaults to 1.

            search_function (callable, optional): Accepts `session`, `title`,
                `year`, `subject_type` & `yes` and returns item.

            chunk_size (int, optional): Streaming download chunk size in
                kilobytes. Defaults to DEFAULT_CHUNK_SIZE.

            tasks (int, optional): Number of tasks to carry out the download.
                Defaults to DEFAULT_TASKS.

            part_dir (Path | str, optional): Directory for temporarily saving the
                downloaded file-parts to. Defaults to CURRENT_WORKING_DIR.

            part_extension (str, optional): Filename extension for download parts.
                 Defaults to DOWNLOAD_PART_EXTENSION.

            merge_buffer_size (int|None, optional). Buffer size for merging the
                separated files in kilobytes. Defaults to chunk_size.

            auto_mode (bool, optional). Iterate over seasons as well. When limit
                is 1 (default), download entire tv series. Defaults to False.

            format(Literal["filename", "group", "struct"] | None, optional): Ways
                of formating filename and saving the episodes. Defaults to None

                group -> Organize episodes into separate folders based on seasons
                    e.g Merlin/S1/Merlin S1E2.mp4

                struct -> Save episodes in a hierarchical directory structure
                    e.g Merlin (2009)/S1/E1.mp4

        run_kwargs: Other keyword arguments for `MediaFileDownloader.run`

        Returns:
             dict[int, dict[str, DownloadedFile | httpx.Response  |
             list[DownloadedFile | httpx.Response ]]]: Episode number and
             downloaded episode file details and caption files.
        """

        assert_instance(quality, CustomResolutionType, "quality")

        assert callable(search_function), (
            "Value for search_function must be callable "
            f"not {type(search_function)}"
        )

        MediaFileDownloader.series_filename_template = episode_filename_tmpl
        CaptionFileDownloader.series_filename_template = caption_filename_tmpl

        response_jar = {}

        group = False

        match format:
            case "group":
                group = True

            case "struct":
                MediaFileDownloader.series_filename_template = "E{episode}.{ext}"
                CaptionFileDownloader.series_filename_template = (
                    "E{episode}.{lan}.{ext}"
                )
                group = True

        target_tv_series = await search_function(
            self.client_session,
            title=title,
            year=year,
            subject_type=SubjectType.TV_SERIES,
            yes=yes,
        )
        assert isinstance(target_tv_series, ResultsSubjectModel), (
            f"Search function {search_function.__name__} must return an "
            "instance of "
            f"{ResultsSubjectModel} not {type(target_tv_series)}"
        )

        downloadable_files_detail_inst = DownloadableFilesDetail(
            self.client_session, resolution=quality
        )

        subtitle_details_items: list[DownloadedFile] = []

        subtitles_dir = tempfile.mkdtemp() if stream_via else caption_dir

        """
        caption_downloader = CaptionFileDownloader(
            dir=(
                subtitles_dir if stream_via else dir if group else subtitles_dir
            ),
            chunk_size=chunk_size,
            tasks=tasks,
            part_dir=part_dir,
            part_extension=part_extension,
            merge_buffer_size=merge_buffer_size,
            group_series=group,
        )
        """

        media_file_downloader = MediaFileDownloader(
            dir=dir,
            chunk_size=chunk_size,
            tasks=tasks,
            part_dir=part_dir,
            part_extension=part_extension,
            merge_buffer_size=merge_buffer_size,
            group_series=group,
        )

        season_details_inst = SeasonDetails(self.client_session)
        series_resource = await season_details_inst.get_content_model(
            target_tv_series.subject_id
        )

        download_request_params = get_download_tv_series_request_params(
            seasons=series_resource.seasons,
            episode=episode,
            season=season,
            limit=-1 if auto_mode else limit,
        )

        logging.info(
            f"Process overview - total "
            f"episodes to be processed: {download_request_params.total_episodes}"
        )

        for req_params in download_request_params.request_params:
            downloadable_files_detail_inst = DownloadableFilesDetail(
                self.client_session,
                page=req_params.page,
                per_page=req_params.per_page,
                resolution=quality,
            )
            files_detail = await downloadable_files_detail_inst.get_content_model(
                target_tv_series.subject_id,
                release_date=str(target_tv_series.release_date),
            )

            for media_file in files_detail.list[req_params.offset :][
                : req_params.limit
            ]:
                if stream_via:
                    media_player_name_func_map[stream_via](
                        str(media_file.url), subtitle_details_items, subtitles_dir
                    )
                    continue

                media_file_response = await media_file_downloader.run(
                    media_file=media_file,
                    filename=files_detail,
                    **run_kwargs,
                )
                current_episode_details = {}

                current_episode_details["movie"] = media_file_response

                if not response_jar.get(media_file.season):
                    response_jar[media_file.season] = []

                response_jar[media_file.season].append({
                    media_file.episode: current_episode_details
                })
                # TODO: add caption_file with key caption

        return response_jar

    def download_movie_sync(
        self,
        *args,
        **kwargs,
    ) -> tuple[
        DownloadedFile | httpx.Response | None,
        list[DownloadedFile | httpx.Response] | None,
    ]:
        """Synchronously search movie by name and proceed to download or
        stream it."""
        return get_event_loop().run_until_complete(
            self.download_movie(*args, **kwargs)
        )

    def download_tv_series_sync(
        self,
        *args,
        **kwargs,
    ) -> dict[
        int,
        dict[
            str,
            DownloadedFile
            | httpx.Response
            | list[DownloadedFile | httpx.Response],
        ],
    ]:
        """Synchronously search tv-series by name and proceed to download or
        stream its episodes."""
        return get_event_loop().run_until_complete(
            self.download_tv_series(*args, **kwargs)
        )
