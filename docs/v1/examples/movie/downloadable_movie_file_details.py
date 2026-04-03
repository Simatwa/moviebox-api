from moviebox_api.v1 import (
    DownloadableMovieFilesDetail,
    MovieDetails,
    Search,
    Session,
    SubjectType,
)


async def downloadable_movie_file_details():
    client_session = Session()
    search = Search(client_session, "avatar", subject_type=SubjectType.MOVIES)

    search_results = await search.get_content_model()
    target_movie = search_results.first_item

    target_movie_details_instance = MovieDetails(
        target_movie, client_session
    )  # (1)

    target_movie_details_model = (
        await target_movie_details_instance.get_content_model()
    )

    downloadable_files = DownloadableMovieFilesDetail(
        client_session, target_movie_details_model
    )
    downloadable_files_detail = await downloadable_files.get_content_model()

    print(type(downloadable_files_detail))  # (2)

    subtitles = downloadable_files_detail.captions

    videos = downloadable_files_detail.downloads


if __name__ == "__main__":
    import asyncio

    asyncio.run(downloadable_movie_file_details())
