import subprocess

import pytest


def run_system_command(command: str) -> int:
    try:
        result = subprocess.run(
            (
                "python -m moviebox_api v3 " + command
                if not command.startswith("python")
                else command
            ),
            shell=True,
            check=True,
            text=True,
            capture_output=True,
        )
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(e.stderr, e.output, sep="\n")
        return e.returncode


def test_version():
    returncode = run_system_command("python -m moviebox_api --version")
    assert returncode <= 0


@pytest.mark.parametrize(
    argnames=[
        "command",
    ],
    argvalues=[
        ["download-movie --help"],
        ["download-series --help"],
        ["homepage-content --help"],
        ["item-details --help"],
    ],
)
def test_help(command):
    returncode = run_system_command(command)
    assert returncode <= 0


@pytest.mark.parametrize(
    argnames=[
        "command",
    ],
    argvalues=[
        ["download-movie avatar -YT"],
        ["download-movie avatar -YT -x en -x filipino"],
        ["download-movie avatar --dub hi -YT"],
        # ["download-movie war -s education -YT"],
        ["download-movie walker -s music -YT"],
        # ["download-movie king -s anime -YT"],
        ["download-series 'A Knight of the Seven Kingdoms' -s 1 -e 1 -YT"],
        [
            "download-series 'A Knight of the Seven Kingdoms' -s 1 -e 1 "
            "--dub 'Telugu dub' -YT"
        ],
        ["download-series banshee -YT -x en -x filipino"],
        ["download-series banshee -YT -x en -x filipino --dub en"],
    ],
)
def test_download(command):
    returncode = run_system_command(command)
    assert returncode <= 0


@pytest.mark.parametrize(
    argnames=[
        "command",
    ],
    argvalues=[
        ["homepage-content"],
        ["homepage-content --json"],
        ["homepage-content --banner"],
        ["homepage-content --banner --json"],
        ["homepage-content --title 'Hollywood'"],
    ],
)
def test_homepage(command):
    returncode = run_system_command(command)
    assert returncode <= 0


@pytest.mark.parametrize(
    argnames=[
        "command",
    ],
    argvalues=(
        ["item-details Merlin --yes --json"],
        ["item-details Avatar -s MOVIES -Y"],
    ),
)
def test_item_details(command):
    returncode = run_system_command(command)
    assert returncode <= 0
