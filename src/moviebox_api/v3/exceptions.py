from moviebox_api.v1.exceptions import (
    ExhaustedSearchResultsError,
    MovieboxApiException,
    ZeroMediaFileError,
    ZeroSearchResultsError,
)


class ResultsNavigationError(MovieboxApiException): ...
