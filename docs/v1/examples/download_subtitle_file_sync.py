from moviebox_api.v1 import (
    DownloadableMovieFilesDetail,
    MovieDetails,
    Search,
    Session,
    SubjectType,
)
from moviebox_api.v1.download import CaptionFileDownloader


def download_subtitle_file():
    session = Session()
    search = Search(session, "avatar", subject_type=SubjectType.MOVIES)

    search_results = search.get_content_model_sync()
    target_movie = search_results.first_item

    target_movie_details_instance = MovieDetails(target_movie, session)

    target_movie_details_model = (
        target_movie_details_instance.get_content_model_sync()
    )

    downloadable_files = DownloadableMovieFilesDetail(
        session, target_movie_details_model
    )
    downloadable_files_detail = downloadable_files.get_content_model_sync()
    target_caption_file = downloadable_files_detail.english_subtitle_file

    caption_file_downloader = CaptionFileDownloader()

    downloaded_file = caption_file_downloader.run_sync(
        target_caption_file,
        filename=target_movie
    )

    print(downloaded_file.saved_to)


if __name__ == "__main__":
    download_subtitle_file()
