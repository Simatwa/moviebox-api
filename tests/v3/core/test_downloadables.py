import pytest

from moviebox_api.v3.core import DownloadableFilesDetail
from moviebox_api.v3.http_client import MovieBoxHttpClient
from moviebox_api.v3.models.downloadables import RootDownloadableFilesDetailModel


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["subject_id"], (["8906247916759695608"], ["1076625875212323512"])
)
async def test_fetching_downloadable_files_detail(subject_id):
    async with MovieBoxHttpClient() as client_session:
        details = DownloadableFilesDetail(
            client_session,
        )
        contents = await details.get_content(subject_id)
        assert type(contents) is dict

        modelled_contents = await details.get_content_model(subject_id)
        assert isinstance(modelled_contents, RootDownloadableFilesDetailModel)

        async for modelled_contents in details.get_content_model_all(subject_id):
            assert isinstance(modelled_contents, RootDownloadableFilesDetailModel)
