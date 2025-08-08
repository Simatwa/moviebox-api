"""Models for item details extracted from html tags"""

from pydantic import BaseModel, HttpUrl, field_validator

from moviebox_api.helpers import get_absolute_url


class HeaderImageModel(BaseModel):
    """`details.header.images`"""

    type: str
    url: str

    @field_validator("url", mode="before")
    def validate_url(value: str) -> str:
        return get_absolute_url(value) if bool(value) else value


class HeadersModel(BaseModel):
    """`details.header`"""

    title: str
    absolute_url: HttpUrl
    description: str
    url: HttpUrl | str
    theme_color: str
    image: HttpUrl
    video: HttpUrl
    keywords: list[str]
    dns_prefetch: list[HttpUrl] | None = None
    images: list[HeaderImageModel] | None = None

    @field_validator("url", mode="before")
    def validate_url(value: str) -> str:
        return get_absolute_url(value) if bool(value) else value

    @field_validator("keywords", mode="before")
    def validate_keywords(value: str) -> list[str]:
        return value.split(",")


class BasicsModel(BaseModel):
    """`details.basics`"""

    title: str
    # TODO: Add more attrs


class CastModel(BaseModel):
    """`details.casts.0`"""

    img: str
    name: str
    character: str


class ReviewModel(BaseModel):
    """`details.reviews.0"""

    author_img: HttpUrl
    author_name: str
    author_time: str
    message: str


class OthersModel(BaseModel):
    """`details.others`"""

    tip: str
    desc: str


class ItemTagDetailsModel(BaseModel):
    """Whole extracted item details from html tags"""

    headers: HeadersModel
    basics: BasicsModel
    casts: list[CastModel]
    reviews: list[ReviewModel]
    others: OthersModel
