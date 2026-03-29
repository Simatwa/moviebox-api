import pytest

from moviebox_api.v2.core import (
    MovieDetails,
    Search,
    SubjectType,
    TVSeriesDetails,
)
from moviebox_api.v2.download import (
    CaptionFileDownloader,
    DownloadableMovieFilesDetail,
    DownloadableTVSeriesFilesDetail,
    MediaFileDownloader,
)
from moviebox_api.v2.requests import Session


@pytest.mark.asyncio
async def test_download_movie_caption_file():
    session = Session()
    search = Search(session, "avatar", subject_type=SubjectType.MOVIES)

    search_results = await search.get_content_model()
    target_movie = search_results.first_item

    target_movie_details_instance = MovieDetails(session)

    target_movie_details_model = (
        await target_movie_details_instance.get_content_model(target_movie)
    )

    downloadable_files = DownloadableMovieFilesDetail(
        session, target_movie_details_model.subject
    )
    downloadable_files_detail = await downloadable_files.get_content_model()
    target_caption_file = downloadable_files_detail.english_subtitle_file

    caption_file_downloader = CaptionFileDownloader()
    response = await caption_file_downloader.run(
        target_caption_file,
        filename=target_movie.title + "- English.srt",
        test=True,
    )
    assert response.is_success


@pytest.mark.asyncio
async def test_download_movie_file():
    session = Session()
    search = Search(session, "avatar", subject_type=SubjectType.MOVIES)

    search_results = await search.get_content_model()
    target_movie = search_results.first_item

    target_movie_details_instance = MovieDetails(session)

    target_movie_details_model = (
        await target_movie_details_instance.get_content_model(target_movie)
    )

    downloadable_files = DownloadableMovieFilesDetail(
        session, target_movie_details_model.subject
    )
    downloadable_files_detail = await downloadable_files.get_content_model()
    target_media_file = downloadable_files_detail.best_media_file

    media_file_downloader = MediaFileDownloader()
    response = await media_file_downloader.run(
        target_media_file, filename=target_movie.title + ".mp4", test=True
    )
    assert response.is_success


@pytest.mark.asyncio
async def test_download_tv_series_caption_file():
    session = Session()
    search = Search(session, "Merlin", subject_type=SubjectType.TV_SERIES)
    search_results = await search.get_content_model()
    target_series = search_results.first_item

    target_series_details_instance = TVSeriesDetails(session)
    target_series_details_model = (
        await target_series_details_instance.get_content_model(target_series)
    )

    downloadable_files = DownloadableTVSeriesFilesDetail(
        session, target_series_details_model.subject
    )

    downloadable_files_detail = await downloadable_files.get_content_model(
        season=1, episode=1
    )
    target_caption_file = downloadable_files_detail.english_subtitle_file

    caption_file_downloader = CaptionFileDownloader()
    response = await caption_file_downloader.run(
        target_caption_file, filename=target_series, test=True
    )
    assert response.is_success


@pytest.mark.asyncio
async def test_download_tv_series_file():
    session = Session()
    search = Search(session, "Merlin", subject_type=SubjectType.TV_SERIES)
    search_results = await search.get_content_model()
    target_series = search_results.first_item

    target_series_details_instance = TVSeriesDetails(session)
    target_series_details_model = (
        await target_series_details_instance.get_content_model(target_series)
    )

    downloadable_files = DownloadableTVSeriesFilesDetail(
        session, target_series_details_model.subject
    )

    downloadable_files_detail = await downloadable_files.get_content_model(
        season=1, episode=1
    )
    target_media_file = downloadable_files_detail.best_media_file

    media_file_downloader = MediaFileDownloader()
    response = await media_file_downloader.run(
        target_media_file, filename=target_series, test=True
    )
    assert response.is_success
