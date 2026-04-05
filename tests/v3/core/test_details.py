import json

import pytest
from pydantic import BaseModel

from moviebox_api.v3.core import ItemDetails
from moviebox_api.v3.http_client import MovieBoxHttpClient
from moviebox_api.v3.models.details import RootItemDetailsModel


def save(data, filename="research.json", indent=4):

    def dump_pydantic_model(data: BaseModel) -> dict:
        if isinstance(data, BaseModel):
            return data.model_dump()

        return data

    if type(data) is list:
        processed_data = []
        for entry in data:
            processed_data.append(dump_pydantic_model(entry))
        data = processed_data

    else:
        data = dump_pydantic_model(data)

    with open(filename, "w") as fh:
        json.dump(data, fh, indent=indent)


@pytest.mark.asyncio
@pytest.mark.parametrize(["subject_id"], (["8906247916759695608"],))
async def test_item_details_fetching(subject_id):
    async with MovieBoxHttpClient() as client_session:
        search = ItemDetails(
            client_session,
        )
        contents = await search.get_content(subject_id)
        assert type(contents) is dict

        modelled_contents = await search.get_content_model(subject_id)
        assert isinstance(modelled_contents, RootItemDetailsModel)
