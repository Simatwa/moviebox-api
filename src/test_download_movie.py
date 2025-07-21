#!/usrr/bin/python

# NOTE: I use this file to debug the package in Windowe
# machine that I don't have admin privileges to install it systemwide
# using uv

import logging

logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%d-%b-%Y %H:%M:%S",
    level=logging.DEBUG,
)


from moviebox_api.requests import Session
from moviebox_api.core import Search, SubjectType
from moviebox_api.download import DownloadableFilesDetail, MediaFileDownloader
from moviebox_api.utils import get_filesize_string


async def main():
    session = Session()
    search = Search(session, "titanic", subject_type=SubjectType.MOVIES)
    search_results = await search.get_modelled_content()
    target_movie = search_results.items[0]
    # print("Target movie :", target_movie)
    downloadable_files = DownloadableFilesDetail(session, target_movie)
    downloadable_files_detail = await downloadable_files.get_modelled_content()
    target_media_file = downloadable_files_detail.best_media_file

    print(
        f"[{get_filesize_string(target_media_file.size)}]Target media file :",
        target_media_file.resolution,
    )
    media_file_downloader = MediaFileDownloader(target_media_file)
    media_file_saved_to = await media_file_downloader.run(
        filename=target_movie.title + ".mp4", progress_bar=True, test=True
    )
    print(media_file_saved_to)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
