"""Gets the work done - download media"""

from pathlib import Path
from moviebox_api.core import Session
from moviebox_api.download import (
    DownloadableSeriesFilesDetail,
    DownloadableMovieFilesDetail,
    MediaFileDownloader,
    CaptionFileDownloader,
)
from moviebox_api.constants import SubjectType, DEFAULT_CAPTION_LANGUAGE
from moviebox_api.download import resolve_media_file_to_be_downloaded
from moviebox_api.cli.helpers import (
    perform_search_and_get_item,
    get_caption_file_or_raise,
)


class Downloader:
    """Controls the movie/series download process"""

    def __init__(self, session: Session = Session()):
        """Constructor for `Downloader`

        Args:
            session (Session, optional): MovieboxAPI httpx request session . Defaults to Session().
        """
        self._session = session

    async def download_movie(
        self,
        title: str,
        year: int,
        yes: bool,
        dir: Path,
        caption_dir: Path,
        quality: str,
        movie_filename_tmpl,
        caption_filename_tmpl,
        language: tuple = (DEFAULT_CAPTION_LANGUAGE,),
        download_caption: bool = False,
        caption_only: bool = False,
        **kwargs,
    ):
        MediaFileDownloader.movie_filename_generation_template = movie_filename_tmpl
        CaptionFileDownloader.movie_filename_generation_template = caption_filename_tmpl
        target_movie = await perform_search_and_get_item(
            self._session,
            title=title,
            year=year,
            subject_type=SubjectType.MOVIES,
            yes=yes,
        )
        downloadable_details_inst = DownloadableMovieFilesDetail(
            self._session, target_movie
        )
        downloadable_details = await downloadable_details_inst.get_modelled_content()
        target_media_file = resolve_media_file_to_be_downloaded(
            quality, downloadable_details
        )
        subtitles_saved_to = []
        if download_caption or caption_only:
            for lang in language:
                target_caption_file = get_caption_file_or_raise(
                    downloadable_details, lang
                )
                caption_downloader = CaptionFileDownloader(target_caption_file)
                subtitle_saved_to = await caption_downloader.run(
                    target_movie, caption_dir, **kwargs
                )
                subtitles_saved_to.append(subtitle_saved_to)
            if caption_only:
                # terminate
                return (None, subtitles_saved_to)

        movie_downloader = MediaFileDownloader(target_media_file)
        # TODO: Consider downloader.run options
        movie_saved_to = await movie_downloader.run(target_movie, dir, **kwargs)
        return (movie_saved_to, subtitles_saved_to)

    async def download_tv_series(
        self,
        title: str,
        year: int,
        season: int,
        episode: int,
        yes: bool,
        dir: Path,
        caption_dir: bool,
        quality: str,
        episode_filename_tmpl,
        caption_filename_tmpl,
        language: tuple = (DEFAULT_CAPTION_LANGUAGE,),
        download_caption: bool = False,
        caption_only: bool = False,
        limit: int = 1,
        **kwargs,
    ) -> dict[int, dict[str, Path | list[Path]]]:
        MediaFileDownloader.series_filename_generation_template = episode_filename_tmpl
        CaptionFileDownloader.series_filename_generation_template = (
            caption_filename_tmpl
        )

        target_tv_series = await perform_search_and_get_item(
            self._session,
            title=title,
            year=year,
            subject_type=SubjectType.TV_SERIES,
            yes=yes,
        )
        downloadable_files = DownloadableSeriesFilesDetail(
            self._session, target_tv_series
        )
        response = {}

        for episode_count in range(limit):
            current_episode = episode + episode_count
            downloadable_files_detail = await downloadable_files.get_modelled_content(
                season=season, episode=current_episode
            )
            # TODO: Iterate over seasons as well
            current_episode_details = {}
            captions_saved_to = []
            if caption_only or download_caption:
                for lang in language:
                    target_caption_file = get_caption_file_or_raise(
                        downloadable_files_detail, lang
                    )
                    caption_downloader = CaptionFileDownloader(target_caption_file)
                    caption_filename = caption_downloader.generate_filename(
                        target_tv_series, season=season, episode=current_episode
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

            target_media_file = resolve_media_file_to_be_downloaded(
                quality, downloadable_files_detail
            )

            media_file_downloader = MediaFileDownloader(target_media_file)
            filename = media_file_downloader.generate_filename(
                target_tv_series, season=season, episode=current_episode
            )
            tv_series_saved_to = await media_file_downloader.run(
                filename, dir=dir, **kwargs
            )
            current_episode_details["movie_path"] = tv_series_saved_to
            response[current_episode] = current_episode_details

        return response
