"""Provide classes that extracts and model specific movie/tv-series details
from its dedicated page.
"""

import typing as t
from json import loads

from moviebox_api.extractor.exceptions import DetailsExtractionError
from moviebox_api.extractor.helpers import souper
from moviebox_api.extractor.models.json import (
    ItemJsonDetailsModel,
    MetadataModel,
    PostListItemModel,
    PubParamModel,
    ResDataModel,
    ResourceModel,
    SeasonsModel,
    StarsModel,
    SubjectModel,
)
from moviebox_api.extractor.models.tag import (
    BasicsModel,
    CastModel,
    HeadersModel,
    ItemTagDetailsModel,
    OthersModel,
    ReviewModel,
)

__all__ = [
    "TagDetailsExtractor",
    "JsonDetailsExtractor",
    "TagDetailsExtractorModel",
    "JsonDetailsExtractorModel",
]


class TagDetailsExtractor:
    """Extracts specific-item details from html tags of the page

    #### Note:
    - Does not extract season details. Use `JsonDetailsExtractor` instead.
    - Also this extraction method suffers from content restriction
    - e.g "This content is not available on the website. Please download our Android app to access it."
    """

    def __init__(self, content: str):
        """Constructor for `TagDetailsExtractor`

        Args:
            content (str): Html formatted text
        """
        self._content = content
        self.souped_content = souper(content)
        self.souped_content_body = self.souped_content.find("body")

    def __repr__(self) -> str:
        headers = self.extract_headers()
        return (
            f"<{self.__module__}.{self.__class__.__name__} "
            f'title="{headers["title"]}" url="{headers["absolute_url"]}">'
        )

    def __call__(self) -> dict[str, list[str] | dict[str, t.Any]]:
        """Extract all possible contents from the page"""
        return self.details

    @property
    def details(self) -> dict[str, list[str] | dict[str, t.Any]]:
        """Whole content

        - Shortcut for `self.extract_all()`
        """
        return self.extract_all()

    def extract_headers(self, include_extra: bool = True) -> dict[str, str | list[str | dict[str, str]]]:
        """Extracts juicy data from the header section

        Args:
            include_extra (bool, optional): Include further details beyond basic one.

        Returns:
            dict[str, str|list[str|dict[str, str]]]: Extracted header data
        """
        resp = {}
        header = self.souped_content.find("head")
        resp["absolute_url"] = header.find("link", {"hreflang": "en"}).get("href")
        resp["title"] = header.find("title").getText(strip=True)

        def get_meta_content(name: str) -> str:
            return header.find("meta", {"name": name}).get("content")

        resp["description"] = get_meta_content("description")
        resp["url"] = get_meta_content("url")
        resp["theme_color"] = get_meta_content("theme-color")
        resp["image"] = get_meta_content("image")
        resp["video"] = get_meta_content("video")
        resp["keywords"] = get_meta_content("keywords")

        if include_extra:
            resp["dns_prefetch"] = [
                entry.get("href") for entry in header.find_all("link", {"rel": "dns-prefetch"})
            ]

            resp["images"] = [
                {"type": entry.get("type"), "url": entry.get("href")}
                for entry in header.find_all("link", {"as": "image"})
            ]
        return resp

    def extract_basics(self) -> dict:
        """Extracts basic data such as `title`, `duration` etc"""

        resp = {}
        basic_soup = self.souped_content_body.find("div", {"class": "pc-detail-content"})
        resp["title"] = basic_soup.find("h1", {"class": "pc-sub-title ellipsis"}).text

        # small_details_soup = basic_soup.find(
        #    "div", {"class": "flx-ce-sta pc-time-type"}
        # )

        # TODO: Extract running time, country etc

        return resp

    def extract_casts(self) -> list[dict[str, str]]:
        """Extracts characters detail"""

        cast_soup = self.souped_content_body.find("div", {"class": "pc-btm-section flx-sta-sta"})
        cast_staff_soup = cast_soup.find("div", {"class": "pc-staff"})

        cast_staff_details = []

        for entry in cast_staff_soup.find_all("div", {"class": "flx-clm-ce-sta pc-starr-item pointer"}):
            details = {}
            details["img"] = entry.find("img", {"class": "pc-img"}).get("src")
            details["name"] = entry.find("div", {"class": "pc-starring-name"}).text
            details["character"] = entry.find("div", {"class": "pc-starring-director"}).text
            cast_staff_details.append(details)

        return cast_staff_details

    def extract_reviews(
        self,
    ) -> list[dict[str, str]]:
        """Retrieves review details"""

        reviews_soup = self.souped_content_body.find("div", {"class": "pc-reviews-box"})
        review_details = []
        for entry in reviews_soup.find_all("div", {"class": "pc-list-item flx-clm-sta"}):
            details = {}
            details["author_img"] = entry.find("div", {"class": "pc-avator"}).find("img").get("src")
            author_info_soup = entry.find("div", {"class": "pc-author-info"})
            details["author_name"] = author_info_soup.find("h4", {"class": "author-name"}).text
            details["author_time"] = author_info_soup.find("div", {"class": "author-time"}).text
            review_container_soup = entry.find("div", {"class": "pc-reviews-desc-container"})
            details["message"] = review_container_soup.find("div", {"class": "pc-reviews-desc"}).text
            review_details.append(details)

        return review_details

    def extract_others(self) -> dict:
        """This include disclaimer etc"""
        resp = {}
        web_page_soup = self.souped_content_body.find("div", {"class": "web-page"})
        resp["tip"] = web_page_soup.find("div", {"class": "pc-btm-tip"}).text
        resp["desc"] = web_page_soup.find("div", {"class": "desc"}).text
        return resp

    def extract_all(self) -> dict[str, list[str] | dict[str, t.Any]]:
        """Extract all possible contents from the page"""

        return {
            "headers": self.extract_headers(),
            "basics": self.extract_basics(),
            "casts": self.extract_casts(),
            "reviews": self.extract_reviews(),
            "others": self.extract_others(),
        }

    def get_details_extractor_model(self) -> "TagDetailsExtractorModel":
        """Returns object that allows modelling of the extracted details"""
        return TagDetailsExtractorModel(self._content)


class JsonDetailsExtractor:
    """Exracts specific-item details from json-formatted data appended on the page

    #### Note:
    - Extracts whole details available.
    """

    def __init__(self, content: str):
        """Constructor for `JsonDetailsExtractor`

        Args:
            content (str): Html contents of the item page
        """
        self._content = content
        self.details: dict[str, t.Any] = self.extract(content)
        """Whole important extracted details"""

    def __repr__(self) -> str:
        title = self.details["resData"]["metadata"]["title"]
        url = self.details["resData"]["metadata"]["url"]
        return rf'{self.__module__}.{self.__class__.__name__} title="{title}" url="{url}">'

    def __call__(self) -> dict[str, t.Any]:
        """Whole important extracted details"""
        return self.details

    @classmethod
    def extract(self, content: str, whole: bool = False) -> dict[str, t.Any]:
        """Extract item details from its specific page.

        Args:
            content (str): Contents of the specific item page (html).
            whole (bool, optional): Include less important details. Defaults to False.

        Raises:
            DetailsExtractionError: Incase no data extracted

        Returns:
            dict[str, t.Any]: Extracted item details
        """
        try:
            from_script = souper(content).find("script", {"type": "application/json"}).text
            data: list = loads(from_script)
            extracts = []

            def resolve_value(value):
                if type(value) is list:
                    return [resolve_value(data[index] if type(index) is int else index) for index in value]

                elif type(value) is dict:
                    processed_value = {}
                    for k, v in value.items():
                        processed_value[k] = resolve_value(data[v])
                    return processed_value

                return value

            for entry in data:
                if type(entry) is dict:
                    details = {}
                    for key, index in entry.items():
                        details[key] = resolve_value(data[index])

                    extracts.append(details)

            if extracts:
                if whole:
                    return extracts[0]
                else:
                    target_data: dict = extracts[0]["state"][1]
                    return dict(
                        zip(
                            [key[2:] for key in target_data.keys()],  # Remove ^$s
                            target_data.values(),
                        )
                    )
            else:
                raise DetailsExtractionError(
                    "The extraction process completed without any find. Ensure correct content is passed."
                )
        except Exception as e:
            if isinstance(e, DetailsExtractionError):
                raise

            raise DetailsExtractionError(
                "The extraction process completed without any find. Ensure correct content is passed."
            ) from e

    @property
    def data(self) -> dict[str, t.Any]:
        """Key data resources

        Contains key data such as `metadata`, `stars`, `reviews`, `resource.seasons`, `subject` etc

        - Retrieved from `self.details["resData"]`
        """
        return self.details["resData"]

    @property
    def subject(self) -> dict[str, t.Any]:
        """Movie details such as `duration`, `releaseDate` etc

        - Retrieved from `self.data["subject"]`
        """

        return self.data["subject"]

    @property
    def reviews(self) -> list[dict[str, t.Any]]:
        """Reviews only

        - Retrieved from `self.data["postList"]["items"]`
        """
        return self.data["postList"]["items"]

    @property
    def metadata(self) -> dict[str, str]:
        """Item metadata such as `description` etc

        - Retrieved from `self.data["metadata"]`
        """
        return self.data["metadata"]

    @property
    def stars(self) -> list[dict[str, str | int]]:
        """Movie casts

        - Retrieved from `self.data["stars"]`
        """
        return self.data["stars"]

    @property
    def resource(self) -> dict[str, str | list[dict]]:
        """Data includes `seasons`, `source` & `uploadBy`

        - Retrieved from `self.data["resource"]`
        """
        return self.data["resource"]

    @property
    def seasons(
        self,
    ) -> list[dict[str, str | int | list[dict[str, int]]]]:
        """Season details

        - Retrieved from `self.resource["seasons"]`
        """
        return self.resource["seasons"]

    @property
    def page_details(self) -> dict[str, str | bool]:
        """Page details such as `url`, `referer`, `lang` etc

        - Retrieved from `self.data["pubParam"]`
        """

        return self.data["pubParam"]

    def get_details_extractor_model(self) -> "JsonDetailsExtractorModel":
        """Returns object that allows modelling of extracted details"""
        return JsonDetailsExtractorModel(self._content)


class TagDetailsExtractorModel:
    """Extracts item details from html tags and model them"""

    def __init__(self, content: str):
        """Constructor for `TagDetailsExtractorModel`

        Args:
            content (str): Html formatted text
        """
        self.tag_details_extractor: TagDetailsExtractor = TagDetailsExtractor(content)

    @property
    def details(self) -> ItemTagDetailsModel:
        """Modelled extracted item details

        - Shortcut for `self.extract_all()`
        """
        return self.extract_all()

    def extract_headers(self) -> HeadersModel:
        """Extracts and model juicy data from the header section of the page"""
        content = self.tag_details_extractor.extract_headers()
        return HeadersModel(**content)

    def extract_basics(self) -> BasicsModel:
        """Extracts and and model basic data such as `title`, `duration` etc"""
        content = self.tag_details_extractor.extract_basics()
        return BasicsModel(**content)

    def extract_casts(self) -> list[CastModel]:
        """Extracts and model characters detail"""
        contents = self.tag_details_extractor.extract_casts()
        return [CastModel(**cast) for cast in contents]

    def extract_reviews(self) -> list[ReviewModel]:
        """Extracts and model reviews"""
        contents = self.tag_details_extractor.extract_reviews()
        return [ReviewModel(**review) for review in contents]

    def extract_others(self) -> OthersModel:
        """Extracts and model other details"""
        content = self.tag_details_extractor.extract_others()
        return OthersModel(**content)

    def extract_all(self) -> ItemTagDetailsModel:
        """Extract item details from its specific page and form model.

        Raises:
            DetailsExtractionError: Incase no data extracted

        Returns:
            ItemTagDetailsModel: Modelled extracted item details
        """
        content = self.tag_details_extractor.extract_all()
        return ItemTagDetailsModel(**content)


class JsonDetailsExtractorModel:
    """Extracts item details from json-formatted data and models them"""

    def __init__(self, content: str):
        """Constructor for `JsonDetailsExtractorModel`

        Args:
            content (str): Html contents of the item page
        """
        self.json_details_extractor: JsonDetailsExtractor = JsonDetailsExtractor(content)
        self.details: ItemJsonDetailsModel = self.extract(content)

    @classmethod
    def extract(cls, content: str) -> ItemJsonDetailsModel:
        """Extract item details from its specific page and form model.

        Args:
            content (str): Contents of the specific item page (html).

        Raises:
            DetailsExtractionError: Incase no data extracted

        Returns:
            ItemJsonDetailsModel: Modelled extracted item details
        """
        contents = JsonDetailsExtractor.extract(content, whole=False)
        return ItemJsonDetailsModel(**contents)

    @property
    def data(self) -> ResDataModel:
        """Key data resources

        Contains key data such as `metadata`, `stars`, `reviews`, `resource.seasons`, `subject` etc

        - Shortcut for `self.details.resData`
        """
        return self.details.resData

    @property
    def subject(self) -> SubjectModel:
        """Movie details such as `duration`, `releaseDate` etc

        - Shortcut for `self.data.subject`
        """
        return self.data.subject

    @property
    def reviews(self) -> list[PostListItemModel]:
        """Reviews only

        - Shortcut for `self.data.postList.items`
        """
        return self.data.postList.items

    @property
    def metadata(self) -> MetadataModel:
        """Item metadata such as `description` etc

        - Shortcut for `self.data.metadata`
        """

        return self.data.metadata

    @property
    def stars(self) -> list[StarsModel]:
        """Movie casts

        - Shortcut for `self.data.stars`
        """
        return self.data.stars

    @property
    def resource(self) -> ResourceModel:
        """Data includes `seasons`, `source` & `uploadBy`

        - Shortcut for `self.data.resource`
        """
        return self.data.resource

    @property
    def seasons(self) -> list[SeasonsModel]:
        """Season details

        - Shortcut for `self.resource.seasons`
        """
        return self.resource.seasons

    @property
    def page_details(self) -> PubParamModel:
        """Page details such as `url`, `referer`, `lang` etc

        - Shortcut for `self.data.pubParam`
        """

        return self.data.pubParam
