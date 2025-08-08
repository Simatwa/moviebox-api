import subprocess

import pytest


def run_system_command(command: str) -> int:
    try:
        result = subprocess.run(
            "python -m moviebox_api " + command,
            shell=True,
            check=True,
            text=True,
            capture_output=True,
        )
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(e, e.output, sep="\n")
        return e.returncode


def test_version():
    returncode = run_system_command("--version")
    assert returncode <= 0


@pytest.mark.parametrize(
    argnames=[
        "command",
    ],
    argvalues=[
        ["download-movie --help"],
        ["download-series --help"],
        ["mirror-hosts --help"],
        ["homepage-content --help"],
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
        ["download-series merlin -s 1 -e 1 -YT"],
    ],
)
def test_download(command):
    returncode = run_system_command(command)
    assert returncode <= 0


def test_mirror_hosts():
    returncode = run_system_command("mirror-hosts --json")
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
        ["homepage-content --title 'Trending Now🔥'"],
    ],
)
def test_homepage(command):
    returncode = run_system_command(command)
    assert returncode <= 0
