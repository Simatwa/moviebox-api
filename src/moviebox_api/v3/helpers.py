import re
from urllib.parse import urlencode

from moviebox_api.v1.helpers import (
    assert_instance,
    is_valid_search_item,
    process_api_response,
    sanitize_item_name,
)
from moviebox_api.v3.constants import VALID_SUBJECT_ID_PATTERN


def combine_url_path_with_params(path: str, params: dict):
    return f"{path}?{urlencode(params)}"


def validate_subject_id(subject_id: str) -> bool:
    return VALID_SUBJECT_ID_PATTERN.match(subject_id) is not None