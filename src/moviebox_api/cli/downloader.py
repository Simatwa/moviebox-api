"""Gets the work done"""

import click
from pathlib import Path
from moviebox_api import logger
from moviebox_api.core import Search, Session
from moviebox_api.download import (
    DownloadableMovieFilesDetail,
    MediaFileDownloader,
    CaptionFileDownloader,
)
from moviebox_api.constants import SubjectType
from moviebox_api.download import resolve_media_file_to_be_downloaded

session = Session()


class Downloader:
    """Class that carry out the  download - movies/series"""

    def __init__(self):
        """Constructor for `Downloader`
        # TODO: accept timeout parameters etc
        """
        self._session = Session()

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

        search = Search(session, title, SubjectType.MOVIES)
        search_results = await search.get_modelled_content()
        logger.info(f"Query '{title}' yielded {len(search_results.items)} movies.")
        if yes:
            target_movie = search_results.items[0]
        else:
            for movie in search_results.items:
                if click.confirm(f"Download {movie.title} ({movie.releaseDate.year})"):
                    target_movie = movie
                    break
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
