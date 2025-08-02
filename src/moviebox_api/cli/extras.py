"""Contains non-essential cli-commands"""

import click
import rich
from json import dumps

from moviebox_api.constants import MIRROR_HOSTS
from moviebox_api.cli.helpers import command_context_settings


@click.command(context_settings=command_context_settings)
@click.option("-j", "--json", is_flag=True, help="Output details in json format")
def mirror_hosts(json: bool):
    """Discover Moviebox mirror hosts [env: MOVIEBOX_API_HOST]"""

    if json:
        rich.print_json(dumps(dict(details=MIRROR_HOSTS), indent=4))
    else:
        from rich.table import Table

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
