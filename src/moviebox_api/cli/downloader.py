"""Gets the work done - downloads media with flexible flow control"""

from pathlib import Path

from moviebox_api.cli.helpers import (
    get_caption_file_or_raise,
    perform_search_and_get_item,
)
from moviebox_api.constants import (
    CURRENT_WORKING_DIR,
    DEFAULT_CAPTION_LANGUAGE,
    DownloadQualitiesType,
    SubjectType,
    loop,
)
from moviebox_api.core import Session
from moviebox_api.download import (
    CaptionFileDownloader,
    DownloadableMovieFilesDetail,
    DownloadableTVSeriesFilesDetail,
    MediaFileDownloader,
    resolve_media_file_to_be_downloaded,
)
from moviebox_api.helpers import assert_instance
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
        language: tuple = (DEFAULT_CAPTION_LANGUAGE,),
        download_caption: bool = False,
        caption_only: bool = False,
        search_function: callable = perform_search_and_get_item,
        **kwargs,
    ) -> tuple[Path | None, list[Path] | None]:
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

        Returns:
            tuple[Path|None, list[Path]|None]: Path to downloaded movie and downloaded caption files.
        """  # noqa: E501
        MediaFileDownloader.movie_filename_template = movie_filename_tmpl
        CaptionFileDownloader.movie_filename_template = caption_filename_tmpl

        assert callable(search_function), (
            f"Value for search_function must be callable not {type(search_function)}"
        )

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
        subtitles_saved_to = []
        if download_caption or caption_only:
            for lang in language:
                target_caption_file = get_caption_file_or_raise(downloadable_details, lang)
                caption_downloader = CaptionFileDownloader(target_caption_file)
                subtitle_saved_to = await caption_downloader.run(target_movie, caption_dir, **kwargs)
                subtitles_saved_to.append(subtitle_saved_to)
            if caption_only:
                # terminate
                return (None, subtitles_saved_to)

        movie_downloader = MediaFileDownloader(target_media_file)

        movie_saved_to = await movie_downloader.run(target_movie, dir, **kwargs)
        return (movie_saved_to, subtitles_saved_to)

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
        **kwargs,
    ) -> dict[int, dict[str, Path | list[Path]]]:
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

        Returns:
            dict[int, dict[str, Path | list[Path]]]: Episode number and path to downloaded episode file and caption files.
        """  # noqa: E501
        MediaFileDownloader.series_filename_template = episode_filename_tmpl
        CaptionFileDownloader.series_filename_template = caption_filename_tmpl

        assert callable(search_function), (
            f"Value for search_function must be callable not {type(search_function)}"
        )

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

        for episode_count in range(limit):
            current_episode = episode + episode_count
            downloadable_files_detail = await downloadable_files.get_content_model(
                season=season, episode=current_episode
            )
            # TODO: Iterate over seasons as well
            current_episode_details = {}
            captions_saved_to = []
            if caption_only or download_caption:
                for lang in language:
                    target_caption_file = get_caption_file_or_raise(downloadable_files_detail, lang)
                    caption_downloader = CaptionFileDownloader(target_caption_file)
                    caption_filename = caption_downloader.generate_filename(
                        target_tv_series,
                        season=season,
                        episode=current_episode,
                    )
                    caption_saved_to = await caption_downloader.run(
                        caption_filename, dir=caption_dir, **kwargs
                    )
                    captions_saved_to.append(caption_saved_to)
                if caption_only:
                    # Avoid downloading tv-series
                    continue

            # Download series

            current_episode_details["captions_path"] = captions_saved_to

            target_media_file = resolve_media_file_to_be_downloaded(quality, downloadable_files_detail)

            media_file_downloader = MediaFileDownloader(target_media_file)
            filename = media_file_downloader.generate_filename(
                target_tv_series,
                season=season,
                episode=current_episode,
            )
            tv_series_saved_to = await media_file_downloader.run(filename, dir=dir, **kwargs)
            current_episode_details["movie_path"] = tv_series_saved_to
            response[current_episode] = current_episode_details

        return response

    def download_movie_sync(
        self,
        *args,
        **kwargs,
    ) -> tuple[Path | None, list[Path] | None]:
        """Synchronously search movie by name and proceed to download it."""
        return loop.run_until_complete(self.download_movie(*args, **kwargs))

    def download_tv_series_sync(
        self,
        *args,
        **kwargs,
    ) -> dict[int, dict[str, Path | list[Path]]]:
        """Synchronously search tv-series by name and proceed to download its episodes."""
        return loop.run_until_complete(self.download_tv_series(*args, **kwargs))
