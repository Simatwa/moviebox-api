import click

from moviebox_api.utils import build_command_group
from moviebox_api.v1.cli.interface import get_commands_map
from moviebox_api.v2.cli.interface import get_commands_map as get_commmands_map_2


@click.group()
@click.version_option(package_name="moviebox-api")
def cli_entry():
    """Search and download movies/tv-series and their subtitles.
    envvar-prefix : MOVIEBOX"""


@cli_entry.group()
def v1():
    """Search and download movies/tv-series and their subtitles"""


@cli_entry.group()
def v2():
    """Search and download movies/tv-series and their subtitles"""


build_command_group(v1, get_commands_map())
build_command_group(v2, get_commmands_map_2())
