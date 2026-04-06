from moviebox_api.v1.exceptions import (
    ExhaustedSearchResultsError,
    MovieboxApiException,
    ZeroSearchResultsError,
)


class ResultsNavigationError(MovieboxApiException): ...
