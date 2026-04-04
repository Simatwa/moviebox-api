from pydantic import ConfigDict

MODEL_CONFIG = ConfigDict(
    populate_by_name=True,
    extra="forbid",
)
