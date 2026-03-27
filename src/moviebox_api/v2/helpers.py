import moviebox_api.v1.helpers
from moviebox_api.v2.constants import HOST_URL


def get_absolute_url(relative_url: str, base_url: str = HOST_URL):

    return moviebox_api.v1.helpers.get_absolute_url(
        relative_url,
        base_url
    )