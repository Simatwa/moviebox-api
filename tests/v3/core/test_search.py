import json

import pytest
from pydantic import BaseModel

from moviebox_api.v3.constants import SubjectType
from moviebox_api.v3.core import Search
from moviebox_api.v3.http_client import MovieBoxHttpClient


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
        search = Search(client_session, 'titanic', subject_type=SubjectType.MOVIES)
        contents = await search.get_content()
        save(contents)