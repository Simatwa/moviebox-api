from moviebox_api.v1 import (
    DownloadableMovieFilesDetail,
    MovieDetails,
    Search,
    Session,
    SubjectType,
)


def downloadable_movie_file_details():
    client_session = Session()
    search = Search(client_session, "avatar", subject_type=SubjectType.MOVIES)

    search_results = search.get_content_model_sync()
    target_movie = search_results.first_item

    target_movie_details_instance = MovieDetails(
        target_movie, client_session
    )  # (1)

    target_movie_details_model = (
        target_movie_details_instance.get_content_model_sync()
    )

    downloadable_files = DownloadableMovieFilesDetail(
        client_session, target_movie_details_model
    )
    downloadable_files_detail = downloadable_files.get_content_model_sync()

    print(type(downloadable_files_detail))  # (2)

    subtitles = downloadable_files_detail.captions

    videos = downloadable_files_detail.downloads


if __name__ == "__main__":
    downloadable_movie_file_details()
