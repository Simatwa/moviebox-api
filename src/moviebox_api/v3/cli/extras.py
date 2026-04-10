"""Contains non-essential cli-commands"""

import click
import rich
from rich.table import Table

from moviebox_api.v3.cli.helpers import (
    command_context_settings,
    perform_search_and_get_item,
    prepare_start,
)
from moviebox_api.v3.constants import SubjectType
from moviebox_api.v3.core import (
    Homepage,
    ItemDetails,
)
from moviebox_api.v3.helpers import get_event_loop
from moviebox_api.v3.http_client import MovieBoxHttpClient
from moviebox_api.v3.models.details import RootItemDetailsModel
from moviebox_api.v3.models.homepage import RootHomepageModel


@click.command(context_settings=command_context_settings)
@click.option("-J", "--json", is_flag=True, help="Output details in json format")
@click.option(
    "-V",
    "--verbose",
    count=True,
    help="Show more detailed interactive texts",
    default=0,
)
@click.option(
    "-Q",
    "--quiet",
    is_flag=True,
    help="Disable showing interactive texts on the progress (logs)",
)
def mirror_hosts_command(json: bool, **start_kwargs):
    """Discover Moviebox mirror hosts [env: MOVIEBOX_API_HOST]"""
    prepare_start(**start_kwargs)

    if json:
        rich.print_json(data=dict(details=MIRROR_HOSTS), indent=4)
    else:
        table = Table(
            title="Moviebox mirror hosts",
            show_lines=True,
        )
        table.add_column("No.", style="white", justify="center")
        table.add_column("Mirror Host", style="cyan", justify="left")

        for no, mirror_host in enumerate(MIRROR_HOSTS, 1):
            table.add_row(str(no), mirror_host)

        rich.print(table)


@click.command(context_settings=command_context_settings)
@click.option(
    "-J",
    "--json",
    is_flag=True,
    help="Output details in json format : False",
)
@click.option(
    "-T",
    "--title",
    help="Title filter for the contents to list : None",
)
@click.option(
    "-B",
    "--banner",
    is_flag=True,
    help="Show banner content only : False",
)
@click.option(
    "-V",
    "--verbose",
    count=True,
    help="Show more detailed interactive texts",
    default=0,
)
@click.option(
    "-Q",
    "--quiet",
    is_flag=True,
    help="Disable showing interactive texts on the progress (logs)",
)
def homepage_content_command(
    json: bool, title: str, banner: bool, **start_kwargs
):
    """Show contents displayed at landing page"""
    # TODO: Add automated test for this command
    prepare_start(**start_kwargs)

    homepage = Homepage(MovieBoxHttpClient())
    homepage_contents: RootHomepageModel = homepage.get_content_model_sync()
    banners: dict[str, list[list[str]]] = {}
    items: dict[str, list[list[str]]] = {}

    for operating in homepage_contents.items:
        if operating.type == "BANNER":
            banners[operating.title] = [
                [
                    item.subject.subject_type.name,
                    item.subject.title,
                    ", ".join(item.subject.genre),
                    str(item.subject.release_date),
                ]
                for item in operating.banner.banners
                if item.subject is not None
            ]

        elif operating.type == "SUBJECTS_MOVIE":
            items[operating.title] = (
                [
                    subject.subject_type.name,
                    subject.title,
                    ", ".join(subject.genre),
                    str(subject.imdb_rating_value),
                    subject.country_name,
                    str(subject.release_date),
                ]
                for subject in operating.subjects
            )
    if json:
        if banner:
            rich.print_json(data=banners, indent=4)

        else:
            processed_items = {}

            for key, value in items.items():
                item_values = []

                for item in value:
                    item_values.append(item)
                processed_items[key] = item_values

            if title is not None:
                assert title in processed_items.keys(), (
                    "Title filter '{title}' is not one of "
                    f"{list(processed_items.keys())}"
                )

                rich.print_json(
                    data={title: processed_items.get(title)}, indent=4
                )
            else:
                rich.print_json(data=processed_items, indent=4)
    else:
        if banner:
            for key in banners.keys():
                target_banner = banners[key]
                table = Table(
                    title=f"{key} - Banner",
                    show_lines=True,
                )
                table.add_column("Pos")
                table.add_column(
                    "Subject type", style="white"
                )  # justify="center")
                table.add_column("Title", style="cyan")

                table.add_column("Genre")
                table.add_column("Release date")
                table.add_column("IMDB Rating")

                for pos, item in enumerate(target_banner, start=1):
                    item.insert(0, str(pos))
                    table.add_row(*item)

                rich.print(table)

        else:
            if title is not None:
                target_title = items.get(title)
                assert target_title is not None, (
                    f"Title filter '{title}' is not one of {list(items.keys())}"
                )
                items = {title: target_title}

            for key in items.keys():
                target_item = items[key]
                table = Table(
                    title=f"{key}",
                    show_lines=True,
                )
                table.add_column("Pos")
                table.add_column("Subject type", style="white")
                table.add_column("Title")

                table.add_column("Genre")
                table.add_column("IMDB Rating")

                table.add_column("Country name")
                table.add_column("Release date")

                for pos, item in enumerate(target_item, start=1):
                    item.insert(0, str(pos))
                    table.add_row(*item)

                rich.print(table)


@click.command(context_settings=command_context_settings)
@click.argument("title")
@click.option(
    "-y",
    "--year",
    type=click.INT,
    help="Year filter for the item to proceed with",
    default=0,
    show_default=True,
)
@click.option(
    "-s",
    "--subject-type",
    type=click.Choice(SubjectType.map().keys(), case_sensitive=False),
    help="Item subject-type filter",
    default=SubjectType.ALL.name,
    show_default=True,
)
@click.option(
    "-Y",
    "--yes",
    is_flag=True,
    help="Do not prompt for item confirmation",
)
@click.option(
    "-J",
    "--json",
    is_flag=True,
    help="Output details in json format instead of tabulated",
)
@click.option(
    "-V",
    "--verbose",
    count=True,
    help="Show more detailed interactive texts",
    default=0,
)
@click.option(
    "-Q",
    "--quiet",
    is_flag=True,
    help="Disable showing interactive texts on the progress (logs)",
)
def item_details_command(json: bool, verbose: int, quiet: bool, **item_kwargs):
    """Show details of a particular movie/tv-series"""
    prepare_start(quiet=quiet, verbose=verbose)

    item_kwargs["subject_type"] = getattr(
        SubjectType, item_kwargs.get("subject_type").upper()
    )
    client_session = MovieBoxHttpClient()

    target_item = get_event_loop().run_until_complete(
        perform_search_and_get_item(client_session, **item_kwargs)
    )

    is_tv_series = target_item.subject_type is SubjectType.TV_SERIES

    item_details = ItemDetails(
        client_session,
        include_seasons=is_tv_series,
    )

    modelled_details: RootItemDetailsModel = item_details.get_content_model_sync()
    details = modelled_details.model_dump(mode="json", by_alias=False)

    season_items = []

    if is_tv_series:
        for season in details["seasons"]:
            season_string = (
                f"Season: {season['se']}, "
                f"Episodes: {season['max_ep']}, "
                f"Resolutions: {[res['resolution'] for res in season['resolutions']]}"
            )
            season_items.append(season_string)

        details["seasons"] = season_items

    if json:
        rich.print_json(data=details, indent=4)

    else:
        table = Table(
            "Key", "Value", title=f"{details['title']} - details", show_lines=True
        )

        for key, value in details.items():
            table.add_row(
                key, "\n".join(value) if type(value) is list else str(value)
            )

        rich.print(table)
