import json

from pydantic import BaseModel


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
