"""Contains non-essentail cli-commands"""

import click
from moviebox_api.cli.helpers import command_context_settings


@click.command(context_settings=command_context_settings)
@click.option("-j", "--json", is_flag=True, help="Output details in json format")
def mirror_hosts(json: bool):
    """Discover moviebox mirror hosts [env: MOVIEBOX_API_HOST]"""
    # Import stuffs here so as to make cli fast
    from moviebox_api.constants import mirror_hosts
    from json import dumps
    import rich

    if json:
        rich.print_json(dumps(dict(details=mirror_hosts), indent=4))
    else:
        from rich.table import Table

        table = Table(
            title="Help info",
            show_lines=True,
        )
        table.add_column("No.", style="white", justify="center")
        table.add_column("Mirror Host", style="cyan", justify="left")

        for no, mirror_host in enumerate(mirror_hosts, 1):
            table.add_row(str(no), mirror_host)
        rich.print(table)


# TODO: Add command for showing accessible mirror hosts
