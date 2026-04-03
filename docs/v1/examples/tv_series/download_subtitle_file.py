from moviebox_api.v1 import (
    DownloadableTVSeriesFilesDetail,
    Search,
    Session,
    SubjectType,
    TVSeriesDetails,
)
from moviebox_api.v1.download import CaptionFileDownloader


async def download_tv_series_subtitle_file():
    client_session = Session()
    search = Search(client_session, "Merlin", subject_type=SubjectType.TV_SERIES)
    search_results = await search.get_content_model()
    target_series = search_results.first_item

    target_series_details_instance = TVSeriesDetails(
        target_series, client_session
    )
    target_series_details_model = (
        await target_series_details_instance.get_content_model()
    )

    downloadable_files = DownloadableTVSeriesFilesDetail(
        client_session, target_series_details_model
    )
    downloadable_files_detail = await downloadable_files.get_content_model(
        season=1, episode=1
    )
    target_media_file = downloadable_files_detail.english_subtitle_file

    caption_file_downloader = CaptionFileDownloader()
    downloaded_file = await caption_file_downloader.run(
        target_media_file, filename=target_series, season=1, episode=1
    )

    print(downloaded_file.saved_to)


if __name__ == "__main__":
    import asyncio

    asyncio.run(download_tv_series_subtitle_file())
