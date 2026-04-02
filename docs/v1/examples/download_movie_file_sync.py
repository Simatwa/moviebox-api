from moviebox_api.v1 import (
    DownloadableMovieFilesDetail,
    MovieDetails,
    Search,
    Session,
    SubjectType,
)
from moviebox_api.v1.download import MediaFileDownloader


def download_movie_file():
    client_session = Session()
    search = Search(client_session, "avatar", subject_type=SubjectType.MOVIES)
    search_results = search.get_content_model_sync()
    target_movie = search_results.first_item

    target_movie_details_instance = MovieDetails(target_movie, client_session)
    target_movie_details_model = (
        target_movie_details_instance.get_content_model_sync()
    )

    downloadable_files = DownloadableMovieFilesDetail(
        client_session, target_movie_details_model
    )
    downloadable_files_detail = downloadable_files.get_content_model_sync()
    target_media_file = downloadable_files_detail.best_media_file

    media_file_downloader = MediaFileDownloader()
    downloaded_file = media_file_downloader.run_sync(
        target_media_file,
        filename=target_movie,
    )

    print(downloaded_file.saved_to)


if __name__ == "__main__":
    download_movie_file()
