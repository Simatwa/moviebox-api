"""Gets the work done - downloads media with flexible flow control"""

import logging
import tempfile
from pathlib import Path
from typing import Literal

import httpx
from throttlebuster import DownloadedFile
from throttlebuster.constants import DOWNLOAD_PART_EXTENSION

from moviebox_api.cli.helpers import (
    get_caption_file_or_raise,
    media_player_name_func_map,
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
from moviebox_api.core import Session, TVSeriesDetails
from moviebox_api.download import (
    CaptionFileDownloader,
    DownloadableMovieFilesDetail,
    DownloadableTVSeriesFilesDetail,
    MediaFileDownloader,
    resolve_media_file_to_be_downloaded,
)
from moviebox_api.exceptions import ZeroCaptionFileError
from moviebox_api.helpers import assert_instance, assert_membership, get_event_loop
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
        stream_via: Literal["mpv", "vlc"] | None = None,
        search_function: callable = perform_search_and_get_item,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        tasks: int = DEFAULT_TASKS,
        part_dir: Path | str = CURRENT_WORKING_DIR,
        part_extension: str = DOWNLOAD_PART_EXTENSION,
        merge_buffer_size: int | None = None,
        ignore_missing_caption: bool = False,
        **run_kwargs,
    ) -> tuple[
        DownloadedFile | httpx.Response | None,
        list[DownloadedFile | httpx.Response] | None,
    ]:
        """Search movie by name and proceed to download it or stream it.

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
            stream_via (Literal["mpv", "vlc"] | None = None, optional): Stream directly in chosen media_player instead of downloading. Defaults to None.
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

        subtitle_details_items: list[DownloadedFile] = []

        subtitles_dir = tempfile.mkdtemp() if stream_via else caption_dir

        if download_caption or caption_only:
            for lang in language:
                try:
                    target_caption_file = get_caption_file_or_raise(downloadable_details, lang)

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
        stream_via: Literal["mpv", "vlc"] | None = None,
        limit: int = 1,
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
            dict[str, DownloadedFile | httpx.Response | list[DownloadedFile | httpx.Response]],
        ],
    ]:
        """Search tv-series by name and proceed to download or stream its episodes.

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
            stream_via (Literal["mpv", "vlc"], optional): Stream directly in chosen media played instead of downloading. Defaults to None.
            limit (int, optional): Number of episodes to download including the offset episode. Defaults to 1.
            search_function (callable, optional): Accepts `session`, `title`, `year`, `subject_type` & `yes` and returns item.
            chunk_size (int, optional): Streaming download chunk size in kilobytes. Defaults to DEFAULT_CHUNK_SIZE.
            tasks (int, optional): Number of tasks to carry out the download. Defaults to DEFAULT_TASKS.
            part_dir (Path | str, optional): Directory for temporarily saving the downloaded file-parts to. Defaults to CURRENT_WORKING_DIR.
            part_extension (str, optional): Filename extension for download parts. Defaults to DOWNLOAD_PART_EXTENSION.
            merge_buffer_size (int|None, optional). Buffer size for merging the separated files in kilobytes. Defaults to chunk_size.
            auto_mode (bool, optional). Iterate over seasons as well. When limit is 1 (default), download entire tv series. Defaults to False.
            format(Literal["filename", "group", "struct"] | None, optional): Ways of formating filename and saving the episodes. Defaults to None
                group -> Organize episodes into separate folders based on seasons e.g Merlin/S1/Merlin S1E2.mp4
                struct -> Save episodes in a hierarchical directory structure e.g Merlin (2009)/S1/E1.mp4

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

        group = False

        match format:
            case "group":
                group = True

            case "struct":
                MediaFileDownloader.series_filename_template = "E{episode}.{ext}"
                CaptionFileDownloader.series_filename_template = "E{episode}.{lan}.{ext}"
                group = True

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

        subtitles_dir = tempfile.mkdtemp() if stream_via else caption_dir

        caption_downloader = CaptionFileDownloader(
            dir=dir if group else subtitles_dir,
            chunk_size=chunk_size,
            tasks=tasks,
            part_dir=part_dir,
            part_extension=part_extension,
            merge_buffer_size=merge_buffer_size,
            group_series=group,
        )

        media_file_downloader = MediaFileDownloader(
            dir=dir,
            chunk_size=chunk_size,
            tasks=tasks,
            part_dir=part_dir,
            part_extension=part_extension,
            merge_buffer_size=merge_buffer_size,
            group_series=group,
        )

        core_tv_series_details = TVSeriesDetails(target_tv_series, self._session)

        tv_series_details_model = await core_tv_series_details.get_json_details_extractor_model()
        series_resource = tv_series_details_model.resource

        async def download_episodes_per_season(
            season_number: int,
            first_episode_number: int,
            episode_limit: int,
        ):
            response = {}
            for episode_count in range(episode_limit):
                current_episode = first_episode_number + episode_count

                downloadable_files_detail = await downloadable_files.get_content_model(
                    season=season_number, episode=current_episode
                )

                current_episode_details = {}
                caption_details_items: list[DownloadedFile] = []

                if caption_only or download_caption:
                    for lang in language:
                        try:
                            target_caption_file = get_caption_file_or_raise(downloadable_files_detail, lang)

                        except (ZeroCaptionFileError, ValueError):
                            if ignore_missing_caption:
                                continue
                            raise

                        caption_details = await caption_downloader.run(
                            caption_file=target_caption_file,
                            filename=target_tv_series,
                            season=season_number,
                            episode=current_episode,
                            **run_kwargs,
                        )

                        caption_details_items.append(caption_details)

                    if caption_only and not stream_via:
                        # Avoid downloading tv-series
                        continue

                # Download or stream series

                current_episode_details["captions"] = caption_details_items

                target_media_file = resolve_media_file_to_be_downloaded(quality, downloadable_files_detail)

                if stream_via:
                    media_player_name_func_map[stream_via](
                        str(target_media_file.url), caption_details_items, subtitles_dir
                    )

                    continue

                tv_series_details = await media_file_downloader.run(
                    media_file=target_media_file,
                    filename=target_tv_series,
                    season=season_number,
                    episode=current_episode,
                    **run_kwargs,
                )

                current_episode_details["movie"] = tv_series_details
                response[current_episode] = current_episode_details

            return response

        if auto_mode:
            if series_resource.total_seasons < season:
                raise RuntimeError(
                    f"The target season {season} exceeds the available "
                    f"tv series seasons {series_resource.total_seasons}."
                )

            total_episodes = 0
            downloaded_episodes_count = 0
            response_jar = {}

            target_seasons = series_resource.seasons[season - 1 :]

            for index, series_season in enumerate(target_seasons):
                new_episodes_count = series_season.maxEp

                if index == 0:
                    # episode offset
                    if series_season.maxEp < episode:
                        raise RuntimeError(
                            f"The target episode offset {episode} for season {series_season.se}"
                            f" is greater than the available episodes {series_season.maxEp}"
                        )

                    else:
                        new_episodes_count -= episode - 1

                total_episodes += new_episodes_count

            if limit != 1:
                if limit > total_episodes:
                    logging.warning(
                        f"You have set total episodes limit to {limit} but only {total_episodes} "
                        f"episodes are available starting from the offset ({season=}, {episode=}"
                        "). The former will be ignored."
                    )
                    limit = total_episodes

            else:
                limit = total_episodes

            logging.info(
                f"Process overview - Seasons: {len(target_seasons)}, total episodes: {total_episodes}, "
                f"episodes download limit: {limit} "
            )

            for index, target_season in enumerate(target_seasons):
                if index == 0:
                    first_episode_number = episode  # declared by user
                    episodes_limit = target_season.maxEp - (episode - 1)  # 1 = index 0

                    if episodes_limit > limit:
                        episodes_limit = limit

                else:
                    first_episode_number = 1

                    remaining_episodes_amount = limit - downloaded_episodes_count

                    if target_season.maxEp > remaining_episodes_amount:
                        episodes_limit = remaining_episodes_amount

                    else:
                        episodes_limit = target_season.maxEp

                downloaded_episodes_details = await download_episodes_per_season(
                    season_number=target_season.se,
                    first_episode_number=first_episode_number,
                    episode_limit=episodes_limit,
                )
                response_jar[target_season.se] = downloaded_episodes_details

                downloaded_episodes_count += episodes_limit

            return response_jar

        else:
            target_season = series_resource.get_season_by_number(season)

            assert episode <= target_season.maxEp, (
                f"The chosen episode offset {episode} exceeds the available episodes {target_season.maxEp}"
            )

            available_episodes = target_season.maxEp - (episode - 1)  # offset

            if limit > available_episodes:
                logging.warning(
                    f"You have set episodes limit to {limit} but only {available_episodes} "
                    f"episodes are available for season {season}, starting from the offset {episode}. "
                    "The former will be ignored."
                )
                limit = available_episodes

            logging.info(
                f"Season {target_season.se} details - Total episodes: {target_season.maxEp}, "
                f"episodes download limit: {limit}"
            )

            downloaded_tv_series_details = await download_episodes_per_season(
                season_number=season, first_episode_number=episode, episode_limit=limit
            )

            return {season: downloaded_tv_series_details}

    def download_movie_sync(
        self,
        *args,
        **kwargs,
    ) -> tuple[
        DownloadedFile | httpx.Response | None,
        list[DownloadedFile | httpx.Response] | None,
    ]:
        """Synchronously search movie by name and proceed to download or stream it."""
        return get_event_loop().run_until_complete(self.download_movie(*args, **kwargs))

    def download_tv_series_sync(
        self,
        *args,
        **kwargs,
    ) -> dict[
        int,
        dict[str, DownloadedFile | httpx.Response | list[DownloadedFile | httpx.Response]],
    ]:
        """Synchronously search tv-series by name and proceed to download or stream its episodes."""
        return get_event_loop().run_until_complete(self.download_tv_series(*args, **kwargs))
