"""Extracts extra movie data from a specific movie page
"""

import typing as t

from moviebox_api.requests import Session
from moviebox_api.models import SearchResultsItem
from moviebox_api.extractor._core import BaseMovieDetailsExtractor


class MovieDetailsExtractor:
    """Extracts further movie details as shown in specific page"""

    def __init__(self, session: Session, search_results_item: SearchResultsItem):
        """Get

        Args:
            session (Session): _description_
            search_results_item (SearchResultsItem): _description_
        """
        # Model the extracted data
