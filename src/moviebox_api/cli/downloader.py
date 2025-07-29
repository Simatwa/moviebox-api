"""Gets the work done"""

import click
from pathlib import Path
from moviebox_api import logger
from moviebox_api.core import Search, Session
from moviebox_api.download import (
    DownloadableSeriesFilesDetail,
    DownloadableMovieFilesDetail,
    MediaFileDownloader,
    CaptionFileDownloader,
)
from moviebox_api.constants import SubjectType
from moviebox_api.download import resolve_media_file_to_be_downloaded
from moviebox_api.cli.helpers import perform_search_and_get_item


class MovieDownloader:
    """Controls the movie download process"""

    def __init__(self, session: Session = Session()):
        """Constructor for `MovieDownloader`

        Args:
            session (Session, optional): MovieboxAPI httpx request session . Defaults to Session().
        """
        self._session = session

    async def download_movie(
        self,
        title: str,
        yes: bool,
        dir: Path,
        quality: str,
        language: str = "English",
        download_caption: bool = True,
        caption_only: bool = True,
    ):
        target_movie = await perform_search_and_get_item(self._session, title, SubjectType.MOVIES, yes)
        downloadable_details_inst = DownloadableMovieFilesDetail(
            self._session, target_movie
        )
        downloadable_details = await downloadable_details_inst.get_modelled_content()
        target_media_file = resolve_media_file_to_be_downloaded(
            quality, downloadable_details
        )
        subtitle_saved_to = None
        if download_caption or caption_only:
            target_caption_file = downloadable_details.get_subtitle_by_language(
                language
            )
            if target_caption_file is None:
                language_subtitle_map = (
                    downloadable_details.get_language_short_subtitle_map
                    if len(language) == 2
                    else downloadable_details.get_language_subtitle_map
                )
                raise ValueError(
                    f"There is no caption file for the language '{language}'. "
                    f"Choose from available ones - {', '.join(list(language_subtitle_map().keys()))}"
                )
            caption_downloader = CaptionFileDownloader(target_caption_file)
            subtitle_saved_to = await caption_downloader.run(target_movie, dir)
            if caption_only:
                # terminate
                return (None, subtitle_saved_to)

        movie_downloader = MediaFileDownloader(target_media_file)
        # TODO: Consider downloader.run options
        movie_saved_to = await movie_downloader.run(target_movie, dir)
        return (movie_saved_to, subtitle_saved_to)


class TVSeriesDownloader:
    """Controls the download of tv-series process."""
    # TODO: Implement this

    def __init__(self, session: Session = Session()):
        """Constructor for `MTVSeriesDownloader`

        Args:
            session (Session, optional): MovieboxAPI httpx request session . Defaults to Session().
        """

        self._session = session


    async def download_tv_series(
        self,
        title:str,
        season:int,
            episode:int,
            yes: bool,
            dir: Path,
            quality: str,
            language: str = "English",
            download_caption: bool = True,
            caption_only: bool = True,
            limit:int=1,
            ):

        target_tv_series = await perform_search_and_get_item(self._session, title, SubjectType.TV_SERIES, yes)
        downloadable_files = DownloadableSeriesFilesDetail(self._session, target_tv_series)
        downloadable_files_detail = await downloadable_files.get_modelled_content(
        season=1, episode=1)
        
        if caption_only:
            for _ in range(limit):
                pass
        target_media_file = downloadable_files_detail.best_media_file

        media_file_downloader = MediaFileDownloader(target_media_file)
        filename = media_file_downloader.generate_filename(
        target_tv_series, season=1, episode=1)
        response = await media_file_downloader.run(filename, test=True)