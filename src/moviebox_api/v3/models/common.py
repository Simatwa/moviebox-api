from datetime import date

from pydantic import ConfigDict

MODEL_CONFIG = ConfigDict(
    populate_by_name=True,
    extra="forbid",
)

DEFAULT_DATE = date(1, 1, 1)
