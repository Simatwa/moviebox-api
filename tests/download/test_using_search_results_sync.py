from moviebox_api.core import Search, SubjectType
from moviebox_api.download import (
    CaptionFileDownloader,
    DownloadableMovieFilesDetail,
    DownloadableTVSeriesFilesDetail,
    MediaFileDownloader,
)
from moviebox_api.models import DownloadableFilesMetadata, SearchResultsModel
from moviebox_api.requests import Session


def test_download_movie_caption_file():
    session = Session()
    search = Search(session, "avatar", subject_type=SubjectType.MOVIES)
    search_results: SearchResultsModel = search.get_content_model_sync()
    target_movie = search_results.first_item

    downloadable_files = DownloadableMovieFilesDetail(session, target_movie)
    downloadable_files_detail: DownloadableFilesMetadata = downloadable_files.get_content_model_sync()
    target_caption_file = downloadable_files_detail.english_subtitle_file

    caption_file_downloader = CaptionFileDownloader()
    response = caption_file_downloader.run_sync(
        target_caption_file, filename=target_movie.title + "- English.srt", test=True
    )
    assert response.is_success


def test_download_movie_file():
    session = Session()
    search = Search(session, "avatar", subject_type=SubjectType.MOVIES)
    search_results: SearchResultsModel = search.get_content_model_sync()
    target_movie = search_results.first_item

    downloadable_files = DownloadableMovieFilesDetail(session, target_movie)
    downloadable_files_detail: DownloadableFilesMetadata = downloadable_files.get_content_model_sync()
    target_media_file = downloadable_files_detail.best_media_file

    media_file_downloader = MediaFileDownloader()
    response = media_file_downloader.run_sync(
        target_media_file, filename=target_movie.title + ".mp4", test=True
    )
    assert response.is_success


def test_download_tv_series_caption_file():
    session = Session()
    search = Search(session, "Merlin", subject_type=SubjectType.TV_SERIES)
    search_results: SearchResultsModel = search.get_content_model_sync()
    target_series = search_results.first_item

    downloadable_files = DownloadableTVSeriesFilesDetail(session, target_series)
    downloadable_files_detail: DownloadableFilesMetadata = downloadable_files.get_content_model_sync(
        season=1, episode=1
    )
    target_caption_file = downloadable_files_detail.english_subtitle_file

    caption_file_downloader = CaptionFileDownloader()
    response = caption_file_downloader.run_sync(target_caption_file, filename=target_series, test=True)
    assert response.is_success


def test_download_tv_series_file():
    session = Session()
    search = Search(session, "Merlin", subject_type=SubjectType.TV_SERIES)
    search_results: SearchResultsModel = search.get_content_model_sync()
    target_series = search_results.first_item

    downloadable_files = DownloadableTVSeriesFilesDetail(session, target_series)
    downloadable_files_detail: DownloadableFilesMetadata = downloadable_files.get_content_model_sync(
        season=1, episode=1
    )
    target_media_file = downloadable_files_detail.best_media_file

    media_file_downloader = MediaFileDownloader()
    response = media_file_downloader.run_sync(target_media_file, filename=target_series, test=True)
    assert response.is_success
