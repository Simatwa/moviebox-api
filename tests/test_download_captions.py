from moviebox_api.requests import Session
from moviebox_api.core import Search, SubjectType
from moviebox_api.download import DownloadableFilesDetail, CaptionFileDownloader


async def main():
    session = Session()
    search = Search(session, "avatar", subject_type=SubjectType.MOVIES)
    search_results = await search.get_modelled_content()
    target_movie = search_results.items[0]
    # print("Target movie :", target_movie)
    downloadable_files = DownloadableFilesDetail(session, target_movie)
    downloadable_files_detail = await downloadable_files.get_modelled_content()
    target_caption_file = downloadable_files_detail.english_subtitle_file
    # print("Target caption file :", target_caption_file)
    caption_file_downloader = CaptionFileDownloader(target_caption_file)
    caption_file_saved_to = await caption_file_downloader.run(
        filename=target_movie.title + "- English.srt"
    )
    print(caption_file_saved_to)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
