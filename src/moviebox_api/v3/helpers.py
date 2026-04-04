from urllib.parse import urlencode

from moviebox_api.v1.helpers import (
    assert_instance,
    is_valid_search_item,
    process_api_response,
    sanitize_item_name,
)


def combine_url_path_with_params(path: str, params: dict):
    return f"{path}?{urlencode(params)}"
