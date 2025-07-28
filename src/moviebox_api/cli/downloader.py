import click
from pathlib import Path
from moviebox_api.core import Search, Session
from moviebox_api.download import (
    DownloadableMovieFilesDetail,
    MediaFileDownloader,
    CaptionFileDownloader,
)
from moviebox_api.models import DownloadableFilesMetadata
from moviebox_api.helpers import SubjectType

session = Session()


def resolve_media_file_to_be_downloaded(
    quality: str, downloadable_metadata: DownloadableFilesMetadata
):
    match quality:
        case "best":
            target_metadata = downloadable_metadata.best_media_file
        case "worst":
            target_metadata = downloadable_metadata.worst_media_file
        case "_":
            target_metadata = downloadable_metadata.best_media_file
        # case "480"
        # TODO: Support this
    return target_metadata


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
        download_caption: bool = True,
    ):

        search = Search(session, title, SubjectType.MOVIES)
        search_results = await search.get_modelled_content()
        if yes:
            target_movie = search_results.items[0]
        else:
            for movie in search_results.items:
                if click.confirm(f"Download {movie.title} ({movie.releaseDate.year})"):
                    target_movie = movie
        downloadable_details_inst = DownloadableMovieFilesDetail(
            self._session, target_movie
        )
        downloadable_details = await downloadable_details_inst.get_modelled_content()
        target_media_file = resolve_media_file_to_be_downloaded(
            quality, downloadable_details
        )
        movie_downloader = MediaFileDownloader(target_media_file)
        # TODO: Consider downloader.run options
        movie_saved_to = await movie_downloader.run(target_movie, dir)
        if download_caption:
            caption_downloader = CaptionFileDownloader(
                downloadable_details.english_subtitle_file
            )
            subtitle_saved_to = await caption_downloader.run(target_movie, dir)
        else:
            subtitle_saved_to = None
        return movie_saved_to, subtitle_saved_to
