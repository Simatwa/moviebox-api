"""Extracts data from specific movie/tv-series page"""

from moviebox_api.extractor._core import (
    JsonDetailsExtractor,
    JsonDetailsExtractorModel,
    TagDetailsExtractor,
    TagDetailsExtractorModel,
)
from moviebox_api.extractor.exceptions import DetailsExtractionError

__all__ = [
    "TagDetailsExtractor",
    "JsonDetailsExtractor",
    "TagDetailsExtractorModel",
    "JsonDetailsExtractorModel",
    "DetailsExtractionError",
]
