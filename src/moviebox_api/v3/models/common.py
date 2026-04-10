from datetime import datetime

from pydantic import ConfigDict

MODEL_CONFIG = ConfigDict(
    populate_by_name=True,
    extra="forbid",
)

DEFAULT_DATETIME = datetime(1, 1, 1)
