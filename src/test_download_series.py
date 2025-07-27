import logging

logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%d-%b-%Y %H:%M:%S",
    level=logging.INFO,
)

from moviebox_api.requests import Session
from moviebox_api.core import Search, SubjectType
from moviebox_api.download import (
    DownloadableSeriesFilesDetail,
    MediaFileDownloader,
)


async def main():
    session = Session()
    search = Search(session, "Merlin", subject_type=SubjectType.TV_SERIES)
    search_results = await search.get_modelled_content()
    target_series = search_results.items[0]
    downloadable_files = DownloadableSeriesFilesDetail(session, target_series)
    downloadable_files_detail = await downloadable_files.get_modelled_content(
        season=1, episode=1
    )
    target_media_file = downloadable_files_detail.best_media_file

    media_file_downloader = MediaFileDownloader(target_media_file)
    response = await media_file_downloader.run(filename=target_series, test=True)
    print(response)
    assert response.is_success == True


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
