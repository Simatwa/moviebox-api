from moviebox_api.requests import Session
from moviebox_api.core import Search, SubjectType
from moviebox_api.download import DownloadableFilesDetail, MediaFileDownloader


async def main():
    session = Session()
    search = Search(session, "titanic", subject_type=SubjectType.MOVIES)
    search_results = await search.get_modelled_content()
    target_movie = search_results.items[0]
    # print("Target movie :", target_movie)
    downloadable_files = DownloadableFilesDetail(session, target_movie)
    downloadable_files_detail = await downloadable_files.get_modelled_content()
    target_media_file = downloadable_files_detail.best_media_file
    print("Target media file :", target_media_file.resolution)
    media_file_downloader = MediaFileDownloader(target_media_file)
    media_file_saved_to = await media_file_downloader.run(
        filename=target_movie.title + ".mp4"
    )
    print(media_file_saved_to)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
