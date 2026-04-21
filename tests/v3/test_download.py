import pytest

from moviebox_api.v3.constants import CustomResolutionType
from moviebox_api.v3.core import DownloadableVideoFilesDetail
from moviebox_api.v3.download import (
    MediaFileDownloader,
    resolve_media_file_to_be_downloaded,
)
from moviebox_api.v3.http_client import MovieBoxHttpClient


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["subject_id", "resolution"],
    (
        ["8906247916759695608", CustomResolutionType._1080P],
        ["8906247916759695608", CustomResolutionType._720P],
    ),
)
async def test_download_movie(subject_id: str, resolution: CustomResolutionType):
    async with MovieBoxHttpClient() as client_session:
        details = DownloadableVideoFilesDetail(
            client_session,
        )

        downloadable_files_detail = await details.get_content_model(subject_id)
        target_media_file = resolve_media_file_to_be_downloaded(
            resolution, downloadable_files_detail
        )

        downloader = MediaFileDownloader()

        response = await downloader.run(
            target_media_file, downloadable_files_detail, test=True
        )

        assert response.is_success


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["subject_id", "resolution"],
    (
        ["1076625875212323512", CustomResolutionType._1080P],
        ["1076625875212323512", CustomResolutionType._720P],
    ),
)
async def test_download_tv_series(
    subject_id: str, resolution: CustomResolutionType
):
    async with MovieBoxHttpClient() as client_session:
        details = DownloadableVideoFilesDetail(
            client_session, resolution=resolution
        )

        downloadable_files_detail = await details.get_content_model(subject_id)

        target_media_file = downloadable_files_detail.list[0]

        downloader = MediaFileDownloader()

        response = await downloader.run(
            target_media_file, downloadable_files_detail, test=True
        )

        assert response.is_success
