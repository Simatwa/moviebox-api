from moviebox_api.v1 import (
    DownloadableMovieFilesDetail,
    MovieDetails,
    Search,
    Session,
    SubjectType,
)
from moviebox_api.v1.download import CaptionFileDownloader


async def download_subtitle_file():
    session = Session()
    search = Search(session, "avatar", subject_type=SubjectType.MOVIES)

    search_results = await search.get_content_model()
    target_movie = search_results.first_item

    target_movie_details_instance = MovieDetails(target_movie, session)

    target_movie_details_model = (
        await target_movie_details_instance.get_content_model()
    )

    downloadable_files = DownloadableMovieFilesDetail(
        session, target_movie_details_model
    )
    downloadable_files_detail = await downloadable_files.get_content_model()
    target_caption_file = downloadable_files_detail.english_subtitle_file

    caption_file_downloader = CaptionFileDownloader()

    downloaded_file = await caption_file_downloader.run(
        target_caption_file,
        filename=target_movie
    )

    print(downloaded_file.saved_to)


if __name__ == "__main__":
    import asyncio

    asyncio.run(download_subtitle_file())
