from moviebox_api.v1.exceptions import (
    ExhaustedSearchResultsError,
    MovieboxApiException,
    ZeroCaptionFileError,
    ZeroMediaFileError,
    ZeroSearchResultsError,
)


class ResultsNavigationError(MovieboxApiException): ...


class MissingDubError(MovieboxApiException): ...
