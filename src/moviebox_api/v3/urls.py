"""
URL templates and factories for MovieBox API endpoints.
"""

HOST_POOL: list[str] = [
    "https://api6.aoneroom.com",
    "https://api5.aoneroom.com",
    "https://api4.aoneroom.com",
    "https://api4sg.aoneroom.com",
    "https://api3.aoneroom.com",
    "https://api6sg.aoneroom.com",
    "https://api.inmoviebox.com",
]

DEFAULT_API_BASE: str = HOST_POOL[0]


WEB_API_BASE: str = "https://h5-api.aoneroom.com"
WEB_HOME_PATH: str = "/wefeed-h5api-bff/page-api/home"

WEB_DETAIL_PATHS: list[str] = [
    "/wefeed-h5api-bff/page-api/subject/detail",
    "/wefeed-h5api-bff/page-api/subject/get",
    "/wefeed-h5api-bff/subject-api/get",
]


MAIN_PAGE_PATH: str = "/wefeed-mobile-bff/tab-operating"
SEARCH_PATH: str = "/wefeed-mobile-bff/subject-api/search"
SEARCH_PATH_V2: str = "/wefeed-mobile-bff/subject-api/search/v2"
SUBJECT_GET_PATH: str = "/wefeed-mobile-bff/subject-api/get"  # item details
SEASON_INFO_PATH: str = "/wefeed-mobile-bff/subject-api/season-info"  # seNum etc
PLAY_INFO_PATH: str = "/wefeed-mobile-bff/subject-api/play-info"  # mpd url
RESOURCE_PATH: str = "/wefeed-mobile-bff/subject-api/resource"
EXT_CAPTIONS_PATH: str = "/wefeed-mobile-bff/subject-api/get-ext-captions"


def main_page_url(base: str, page: int = 1, tab_id: int = 0) -> str:
    return f"{base}{MAIN_PAGE_PATH}?page={page}&tabId={tab_id}&version="


def subject_url(base: str, subject_id: str) -> str:
    return f"{base}{SUBJECT_GET_PATH}?subjectId={subject_id}"


def season_info_url(base: str, subject_id: str) -> str:
    return f"{base}{SEASON_INFO_PATH}?subjectId={subject_id}"


def play_info_url(
    base: str, subject_id: str, season: int = 0, episode: int = 0
) -> str:
    return (
        f"{base}{PLAY_INFO_PATH}?subjectId={subject_id}&se={season}&ep={episode}"
    )


def resource_url(base: str, subject_id: str, season: int, episode: int) -> str:
    return (
        f"{base}{RESOURCE_PATH}?subjectId={subject_id}&se={season}&ep={episode}"
    )


def web_detail_url(subject_id: str, path: str) -> str:
    return f"{WEB_API_BASE}{path}?subjectId={subject_id}"
