import json

import pytest
from pydantic import BaseModel

from moviebox_api.v3.core import Homepage
from moviebox_api.v3.http_client import MovieBoxHttpClient
from moviebox_api.v3.models.homepage import RootHomepageModel


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
async def test_homepage_fetch_contents():
    async with MovieBoxHttpClient() as client_session:
        homepage = Homepage(client_session)
        contents = await homepage.get_content()
        assert type(contents) is dict
        modelled_contents = await homepage.get_content_model()
        assert isinstance(modelled_contents, RootHomepageModel)
        save(modelled_contents)
