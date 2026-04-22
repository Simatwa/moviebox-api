"""v2 Exceptions"""

from moviebox_api.v1.exceptions import (
    ExhaustedSearchResultsError,
    MovieboxApiException,
)


class InvalidDetailPathError(MovieboxApiException): ...
