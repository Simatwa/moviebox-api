#!/usrr/bin/python

# NOTE: I use this file to debug the package in Windows
# machine that I don't have admin privileges to install it system-wide
# using uv

import logging

logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%d-%b-%Y %H:%M:%S",
    level=logging.INFO,
)


from moviebox_api.requests import Session
from moviebox_api.core import Search, SubjectType
from moviebox_api.download import DownloadableMovieFilesDetail, MediaFileDownloader

# from moviebox_api.utils import get_filesize_string


async def main():
    session = Session()
    search = Search(session, "Heads of state", subject_type=SubjectType.MOVIES)
    search_results = await search.get_modelled_content()
    target_movie = search_results.items[0]
    # print("Target movie :", target_movie)
    downloadable_files = DownloadableMovieFilesDetail(session, target_movie)
    downloadable_files_detail = await downloadable_files.get_modelled_content()
    target_media_file = downloadable_files_detail.best_media_file
    media_file_downloader = MediaFileDownloader(target_media_file)
    media_file_saved_to = await media_file_downloader.run(
        filename=f"{target_movie.title} - {target_media_file.resolution}p.mp4",
        progress_bar=True,
        test=True,
        # resume=True,  # False,  # True,
        simple=False,
        ascii=False,
    )
    print(media_file_saved_to)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
