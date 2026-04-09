from datetime import datetime

from pydantic import ConfigDict

MODEL_CONFIG = ConfigDict(
    populate_by_name=True,
    extra="forbid",
)

DEFAULT_DATETIME = datetime(2000, 1, 1)
