from urllib.parse import urlencode

from moviebox_api.v1.helpers import assert_instance, process_api_response


def combine_url_path_with_params(path: str, params: dict):
    return f"{path}?{urlencode(params)}"