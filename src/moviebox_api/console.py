import logging
import os
import sys

import click

from moviebox_api.utils import build_command_group
from moviebox_api.v1.cli.helpers import show_any_help
from moviebox_api.v1.cli.interface import get_commands_map
from moviebox_api.v2.cli.interface import get_commands_map as get_commmands_map_2


@click.group()
@click.version_option(package_name="moviebox-api")
def cli_entry():
    """Search and download movies/tv-series and their subtitles.
    envvar-prefix : MOVIEBOX"""


@cli_entry.group()
def v1():
    """Search and download movies/tv-series using moviebox-API v1"""


@cli_entry.group()
def v2():
    """Search and download movies/tv-series etc using moviebox-API v2"""


build_command_group(v1, get_commands_map())
build_command_group(v2, get_commmands_map_2())


def main():
    try:
        return cli_entry()

    except Exception as e:
        exception_msg = str({e.args[1] if e.args and len(e.args) > 1 else e})

        DEBUG = os.getenv("DEBUG", "0") == "1"

        if DEBUG:
            logging.exception(e)
        else:
            if bool(exception_msg):
                logging.error(exception_msg)
            sys.exit(show_any_help(e, exception_msg))

    sys.exit(1)
