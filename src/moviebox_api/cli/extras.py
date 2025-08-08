"""Contains non-essential cli-commands"""

import click
import rich
from rich.table import Table

from moviebox_api.cli.helpers import command_context_settings, loop
from moviebox_api.constants import MIRROR_HOSTS
from moviebox_api.core import Homepage
from moviebox_api.requests import Session


@click.command(context_settings=command_context_settings)
@click.option("-j", "--json", is_flag=True, help="Output details in json format")
def mirror_hosts(json: bool):
    """Discover Moviebox mirror hosts [env: MOVIEBOX_API_HOST]"""

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


# TODO: Add command for showing accessible mirror hosts


@click.command()
@click.option(
    "-j",
    "--json",
    is_flag=True,
    help="Output details in json format : False",
)
@click.option(
    "-t",
    "--title",
    help="Title filter for the contents to list : None",
)
@click.option(
    "-b",
    "--banner",
    is_flag=True,
    help="Show banner content only : False",
)
def homepage_content(json: bool, title: str, banner: bool):
    """Show contents displayed at landing page"""
    # TODO: Add automated test for this command
    session = Session()
    homepage = Homepage(session)
    homepage_contents = loop.run_until_complete(homepage.get_content_model())
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
