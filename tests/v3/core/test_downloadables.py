import pytest

from moviebox_api.v3.core import (
    DownloadableCaptionFileDetails,
    DownloadableVideoFilesDetail,
)
from moviebox_api.v3.http_client import MovieBoxHttpClient
from moviebox_api.v3.models.downloadables import (
    RootCaptionFileMetadata,
    RootDownloadableFilesDetailModel,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["subject_id"], (["8906247916759695608"], ["1076625875212323512"])
)
async def test_fetching_downloadable_video_files_detail(subject_id):
    async with MovieBoxHttpClient() as client_session:
        details = DownloadableVideoFilesDetail(
            client_session,
        )
        contents = await details.get_content(subject_id)
        assert type(contents) is dict

        modelled_contents = await details.get_content_model(subject_id)
        assert isinstance(modelled_contents, RootDownloadableFilesDetailModel)

        async for modelled_contents in details.get_content_model_all(subject_id):
            assert isinstance(modelled_contents, RootDownloadableFilesDetailModel)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["subject_id"], (["8906247916759695608"], ["1076625875212323512"])
)
async def test_fetching_downloadable_caption_file_details(subject_id):
    async with MovieBoxHttpClient() as client_session:
        video_details_inst = DownloadableVideoFilesDetail(
            client_session, per_page=2
        )

        downloadable_videos = await video_details_inst.get_content_model(
            subject_id
        )

        caption_details_inst = DownloadableCaptionFileDetails(client_session)

        for index, target_video in enumerate(downloadable_videos.list):
            caption_details = await caption_details_inst.get_content_model(
                subject_id,
                resource=target_video
                if index % 2 == 0
                else target_video.resource_id,
            )
            assert isinstance(caption_details, RootCaptionFileMetadata)
