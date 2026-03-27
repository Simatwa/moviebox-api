from importlib import metadata

try:
    __version__ = metadata.version("moviebox-api")
except metadata.PackageNotFoundError:
    __version__ = "0.0.0"

__author__ = "Smartwa"
__repo__ = "https://github.com/Simatwa/moviebox-api"