import re
from dataclasses import dataclass, field
from math import ceil, floor
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
from moviebox_api.v3.models.details import SeasonItemModel


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


@dataclass
class RequestParams:
    offset: int
    page: int
    per_page: int  # max - 20
    limit: int


@dataclass
class PaginationDetails:
    total_episodes: int
    request_params: list[RequestParams]


def get_episodes_amount(seasons: list[SeasonItemModel]) -> int:
    return sum(season.total_episodes for season in seasons)


def get_download_tv_series_request_params(
    seasons: list[SeasonItemModel],
    episode: int = 1,
    season: int = 1,
    per_page: int = 20,
    limit: int = -1,
) -> PaginationDetails:
    params: list[RequestParams] = []

    season_numbers = [s.season_number for s in seasons]

    if season not in season_numbers:
        raise ValueError(
            f"Season {season} does not exist. Available seasons: {season_numbers}"
        )

    target_season = next(s for s in seasons if s.season_number == season)
    if episode > target_season.total_episodes:
        raise ValueError(
            f"Episode {episode} exceeds season {season} "
            f"total episodes ({target_season.total_episodes})."
        )

    total_episodes = get_episodes_amount(seasons)
    seasons_before = [s for s in seasons if s.season_number < season]
    offset_episodes = get_episodes_amount(seasons_before) + (
        episode - 1
    )  # -1: episode is 1-based
    available_episodes = total_episodes - offset_episodes

    if limit != -1 and limit > available_episodes:
        raise ValueError(
            f"Limit {limit} exceeds available episodes ({available_episodes}) "
            f"from season {season}, episode {episode}."
        )

    no_offset = episode == 1 and season == season_numbers[0]
    no_limit = limit == -1

    if no_offset and no_limit:
        number_of_pages = ceil(total_episodes / per_page)
        for x in range(number_of_pages):
            page_number = x + 1
            loaded_episodes = per_page * x
            page_limit = min(per_page, total_episodes - loaded_episodes)
            params.append(
                RequestParams(
                    offset=0,
                    page=page_number,
                    per_page=per_page,
                    limit=page_limit,
                )
            )
    else:
        wanted_episodes = available_episodes if no_limit else limit

        offset_page = floor(offset_episodes / per_page)
        offset_in_page = offset_episodes % per_page

        loaded = 0

        if offset_in_page > 0:
            page_limit = min(per_page - offset_in_page, wanted_episodes)
            params.append(
                RequestParams(
                    offset=offset_in_page,
                    page=offset_page + 1,
                    per_page=per_page,
                    limit=page_limit,
                )
            )
            loaded += page_limit

        while loaded < wanted_episodes:
            remaining = wanted_episodes - loaded
            current_page = (
                offset_page
                + ceil((loaded + 1) / per_page)
                + (1 if offset_in_page > 0 else 0)
            )
            page_limit = min(per_page, remaining)
            params.append(
                RequestParams(
                    offset=0,
                    page=current_page,
                    per_page=per_page,
                    limit=page_limit,
                )
            )
            loaded += page_limit

        total_episodes = wanted_episodes

    return PaginationDetails(total_episodes=total_episodes, request_params=params)