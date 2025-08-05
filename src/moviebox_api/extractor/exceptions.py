from moviebox_api._bases import BaseMovieboxException


class DetailsExtractionError(BaseMovieboxException):
    """Raised when trying to extract data from html page without success"""
