import pytest

from moviebox_api.v3.core import (
    DownloadableCaptionFileDetails,
    DownloadableVideoFilesDetail,
)
from moviebox_api.v3.download import CaptionFileDownloader
from moviebox_api.v3.http_client import MovieBoxHttpClient


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["subject_id", "language"],
    (
        ["8906247916759695608", "English"],
        ["8906247916759695608", "en"],
        ["1076625875212323512", "Filipino"],
        ["1076625875212323512", "en"],
    ),
)
async def test_download_caption_file(subject_id: str, language: str):
    async with MovieBoxHttpClient() as client_session:
        video_details_inst = DownloadableVideoFilesDetail(
            client_session, per_page=1
        )

        downloadable_videos = await video_details_inst.get_content_model(
            subject_id
        )

        target_video = downloadable_videos.list[0]

        caption_details_inst = DownloadableCaptionFileDetails(client_session)

        caption_details = await caption_details_inst.get_content_model(
            subject_id, resource=target_video
        )

        target_caption = caption_details.get_subtitle_by_language(language)

        caption_downloader_inst = CaptionFileDownloader()

        resp = await caption_downloader_inst.run(
            caption_file=target_caption,
            video_file=target_video,
            filename=downloadable_videos,
            test=True,
        )

        assert resp.is_success
