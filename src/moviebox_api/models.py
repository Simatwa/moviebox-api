""" 
Models for package level usage.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class MovieboxAppInfo:
    """This data is fetched when requesting for cookies,
    so I just find it important that I expose it in the package
    """
    channelType: str
    pkgName: str
    url: str
    versionCode: str
    versionName: str
