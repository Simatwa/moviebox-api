from moviebox_api.v1 import (
    DownloadableTVSeriesFilesDetail,
    Search,
    Session,
    SubjectType,
    TVSeriesDetails,
)


async def downloadable_tv_series_file_details():
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

    print(type(downloadable_files_detail))  # (1)

    subtitles = downloadable_files_detail.captions

    videos = downloadable_files_detail.downloads


if __name__ == "__main__":
    import asyncio

    asyncio.run(downloadable_tv_series_file_details())
