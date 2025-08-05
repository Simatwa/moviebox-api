"""Extracts data from specific movie/tv-series page
"""

from moviebox_api.extractor._core import TagDetailsExtractor, JsonDetailsExtractor
from moviebox_api.extractor.exceptions import DetailsExtractionError

__all__ = ["TagDetailsExtractor", "JsonDetailsExtractor", "DetailsExtractionError"]
