import re
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from moviebox_api.v1.helpers import (
    assert_instance,
    get_event_loop,
    get_file_extension,
    is_valid_search_item,
    process_api_response,
    sanitize_item_name,
)
from moviebox_api.v3.constants import (
    SEARCH_PER_PAGE_LIMIT,
    VALID_SUBJECT_ID_PATTERN,
)


def combine_url_path_with_params(path: str, params: dict):
    parsed = urlparse(path)

    existing_params = dict(parse_qsl(parsed.query))

    merged_params = {**existing_params, **params}
    new_query = urlencode(merged_params)

    return urlunparse(parsed._replace(query=new_query))


def validate_subject_id(subject_id: str) -> bool:
    return VALID_SUBJECT_ID_PATTERN.match(subject_id) is not None


def validate_per_page_and_raise(per_page: int) -> None:
    assert 0 < per_page <= SEARCH_PER_PAGE_LIMIT, (
        f"per_page value {per_page} is NOT between 0 and {SEARCH_PER_PAGE_LIMIT}"
    )
