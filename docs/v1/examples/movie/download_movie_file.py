from moviebox_api.v1 import (
    DownloadableMovieFilesDetail,
    MovieDetails,
    Search,
    Session,
    SubjectType,
)
from moviebox_api.v1.download import MediaFileDownloader


async def download_movie_file():
    client_session = Session()
    search = Search(client_session, "avatar", subject_type=SubjectType.MOVIES)
    search_results = await search.get_content_model()
    target_movie = search_results.first_item

    target_movie_details_instance = MovieDetails(target_movie, client_session)
    target_movie_details_model = (
        await target_movie_details_instance.get_content_model()
    )

    downloadable_files = DownloadableMovieFilesDetail(
        client_session, target_movie_details_model
    )
    downloadable_files_detail = await downloadable_files.get_content_model()
    target_media_file = downloadable_files_detail.best_media_file

    media_file_downloader = MediaFileDownloader()
    downloaded_file = await media_file_downloader.run(
        target_media_file,
        filename=target_movie,
    )

    print(downloaded_file.saved_to)


if __name__ == "__main__":
    import asyncio

    asyncio.run(download_movie_file())
