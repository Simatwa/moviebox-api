from moviebox_api.v1 import (
    DownloadableTVSeriesFilesDetail,
    Search,
    Session,
    SubjectType,
    TVSeriesDetails,
)
from moviebox_api.v1.download import MediaFileDownloader


def download_tv_series_video_file():
    client_session = Session()
    search = Search(client_session, "Merlin", subject_type=SubjectType.TV_SERIES)
    search_results = search.get_content_model_sync()
    target_series = search_results.first_item

    target_series_details_instance = TVSeriesDetails(
        target_series, client_session
    )
    target_series_details_model = (
        target_series_details_instance.get_content_model_sync()
    )

    downloadable_files = DownloadableTVSeriesFilesDetail(
        client_session, target_series_details_model
    )
    downloadable_files_detail = downloadable_files.get_content_model_sync(
        season=1, episode=1
    )
    target_media_file = downloadable_files_detail.best_media_file  # (1)

    media_file_downloader = MediaFileDownloader()
    downloaded_file = media_file_downloader.run_sync(
        target_media_file, filename=target_series
    )

    print(downloaded_file.saved_to)


if __name__ == "__main__":
    download_tv_series_video_file()
