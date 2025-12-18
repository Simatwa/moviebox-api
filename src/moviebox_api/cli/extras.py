"""Contains non-essential cli-commands"""

import click
import rich
from rich.table import Table

from moviebox_api.cli.helpers import (
    command_context_settings,
    perform_search_and_get_item,
    prepare_start,
)
from moviebox_api.constants import MIRROR_HOSTS, SubjectType
from moviebox_api.core import Homepage, MovieDetails, PopularSearch, TVSeriesDetails
from moviebox_api.extractor import JsonDetailsExtractor
from moviebox_api.helpers import get_event_loop
from moviebox_api.requests import Session


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
def homepage_content_command(json: bool, title: str, banner: bool, **start_kwargs):
    """Show contents displayed at landing page"""
    # TODO: Add automated test for this command
    prepare_start(**start_kwargs)

    session = Session()
    homepage = Homepage(session)
    homepage_contents = get_event_loop().run_until_complete(homepage.get_content_model())

    banners: dict[str, list[list[str]]] = {}
    items: dict[str, list[list[str]]] = {}

    for operating in homepage_contents.operatingList:
        if operating.type == "BANNER":
            banners[operating.title] = [
                [
                    item.subjectType.name,
                    item.title,
                    ", ".join(item.subject.genre),
                    str(item.subject.releaseDate),
                ]
                for item in operating.banner.items
                if item.subject is not None
            ]

        elif operating.type == "SUBJECTS_MOVIE":
            items[operating.title] = (
                [
                    subject.subjectType.name,
                    subject.title,
                    ", ".join(subject.genre),
                    str(subject.imdbRatingValue),
                    subject.countryName,
                    str(subject.releaseDate),
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
                    f"Title filter '{title}' is not one of {list(processed_items.keys())}"
                )

                rich.print_json(data={title: processed_items.get(title)}, indent=4)
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
                table.add_column("Subject type", style="white")  # justify="center")
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
                assert target_title is not None, f"Title filter '{title}' is not one of {list(items.keys())}"
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
@click.option(
    "-J",
    "--json",
    is_flag=True,
    help="Output details in json format : False",
)
def popular_search_command(json: bool):
    """Movies/tv-series many people are searching now"""
    prepare_start()

    search = PopularSearch(Session())
    items = get_event_loop().run_until_complete(search.get_content_model())

    if json:
        processed_items = [item.title for item in items]
        rich.print_json(data=dict(popular=processed_items), indent=4)

    else:
        table = Table(title="Popular Searches Now", show_lines=True)

        table.add_column("Pos")
        table.add_column("Title")

        for pos, item in enumerate(items, start=1):
            table.add_row(str(pos), item.title)

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
    type=click.Choice(SubjectType.map().keys()),
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
@click.option("-F", "--full", is_flag=True, help="Show all details of the item")
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
def item_details_command(json: bool, full: bool, verbose: int, quiet: bool, **item_kwargs):
    """Show details of a particular movie/tv-series"""
    prepare_start(quiet=quiet, verbose=verbose)

    item_kwargs["subject_type"] = getattr(SubjectType, item_kwargs.get("subject_type"))
    session = Session()

    target_item = get_event_loop().run_until_complete(
        perform_search_and_get_item(session=session, **item_kwargs)
    )

    subject_type_item_details_map = {
        SubjectType.MOVIES: MovieDetails,
        SubjectType.TV_SERIES: TVSeriesDetails,
    }

    ItemDetails: MovieDetails | TVSeriesDetails = subject_type_item_details_map.get(target_item.subjectType)

    assert ItemDetails, (
        f"The selected item type - {target_item.subjectType.name} - is not yet supported. "
        "Choose items of subject types "
        f"{' or '.join([key.name for key in list(subject_type_item_details_map.keys())])}"
    )

    item_details = ItemDetails(target_item, session=session)

    extractor = JsonDetailsExtractor(item_details.get_html_content_sync())

    details = target_item.model_dump() if full else {}

    details.update(extractor.metadata)

    season_items = []

    for season in extractor.seasons:
        season_string = (
            f"Season: {season['se']} "
            f"Episodes: {season['maxEp']} "
            f"Resolutions: {[res['resolution'] for res in season['resolutions']]}"
        )
        season_items.append(season_string)

    details["seasons"] = season_items

    if json:
        rich.print_json(data=details, indent=4)

    else:
        table = Table("Key", "Value", title=f"{details['title']} - details", show_lines=True)

        for key, value in details.items():
            table.add_row(key, "\n".join(value) if type(value) is list else str(value))

        rich.print(table)
