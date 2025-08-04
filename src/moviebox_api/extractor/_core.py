"""Contains Base Extractor class"""

import typing as t

from moviebox_api.extractor.helpers import souper


class BaseDetailsExtractor:
    """Performs actual extraction of further movie/tv-series details"""

    def __init__(self, content: str):
        """Constructor for `BaseMovieDetailsExtractor`

        Args:
            content (str): Html formatted text
        """
        self._content = content
        self.souped_content = souper(content)
        self.souped_content_body = self.souped_content.find("body")

    def extract_headers(
        self, include_extra: bool = True
    ) -> dict[str, str | list[str | dict[str, str]]]:
        """Extracts juicy data from the header section

        Args:
            include_extra (bool, optional): Include further details beyond basic one.

        Returns:
            dict[str, str|list[str|dict[str, str]]]: Extracted header data
        """
        resp = {}
        header = self.souped_content.find("head")
        resp["absolute_url"] = header.find("link", {"hreflang": "en"}).get("href")
        resp["title"] = header.find("title").text

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
                entry.get("href")
                for entry in header.find_all("link", {"rel": "dns-prefetch"})
            ]
            resp["images"] = [
                {"type": entry.get("type"), "url": entry.get("href")}
                for entry in header.find_all("link", {"as": "image"})
            ]
        return resp

    def extract_basics(self) -> dict:
        """Extracts basic data such as `title`, `duration` etc"""
        resp = {}
        basic_soup = self.souped_content_body.find(
            "div", {"class": "pc-detail-content"}
        )
        resp["title"] = basic_soup.find("h1", {"class": "pc-sub-title ellipsis"}).text

        # small_details_soup = basic_soup.find(
        #    "div", {"class": "flx-ce-sta pc-time-type"}
        # )

        # TODO: Extract running time, country etc

        return resp

    def extract_casts(self) -> dict[str, str | list[dict[str, str]]]:
        """Extracts actors/actress details"""
        resp = {}

        cast_soup = self.souped_content_body.find(
            "div", {"class": "pc-btm-section flx-sta-sta"}
        )
        cast_staff_soup = cast_soup.find("div", {"class": "pc-staff"})
        resp["intro"] = cast_staff_soup.find("div", {"class": "pc-foryou-title"}).text

        cast_staff_details = []

        for entry in cast_staff_soup.find_all(
            "div", {"class": "flx-clm-ce-sta pc-starr-item pointer"}
        ):
            details = {}
            details["img"] = entry.find("img", {"class": "pc-img"}).get("src")
            details["name"] = entry.find("div", {"class": "pc-starring-name"}).text
            details["character"] = entry.find(
                "div", {"class": "pc-starring-director"}
            ).text
            cast_staff_details.append(details)
        resp["casts"] = cast_staff_details

        return resp

    def extract_reviews(self) -> dict[str, str | list[dict[str, str]]]:
        """Retrieves review details"""
        resp = {}
        reviews_soup = self.souped_content_body.find("div", {"class": "pc-reviews-box"})
        resp["intro"] = reviews_soup.find(
            "h3", {"class": "pc-reviews-tit pc-sec-tit"}
        ).text
        review_details = []

        for entry in reviews_soup.find_all(
            "div", {"class": "pc-list-item flx-clm-sta"}
        ):
            details = {}
            details["author_img"] = (
                entry.find("div", {"class": "pc-avator"}).find("img").get("src")
            )
            author_info_soup = entry.find("div", {"class": "pc-author-info"})
            details["author_name"] = author_info_soup.find(
                "h4", {"class": "author-name"}
            ).text
            details["author_time"] = author_info_soup.find(
                "div", {"class": "author-time"}
            ).text
            review_container_soup = entry.find(
                "div", {"class": "pc-reviews-desc-container"}
            )
            details["message"] = review_container_soup.find(
                "div", {"class": "pc-reviews-desc"}
            ).text
            review_details.append(details)
        resp["reviews"] = review_details
        return resp

    def extract_others(self) -> dict:
        """This include disclaimer etc"""
        resp = {}
        web_page_soup = self.souped_content_body.find("div", {"class": "web-page"})
        resp["tip"] = web_page_soup.find("div", {"class": "pc-btm-tip"}).text
        resp["desc"] = web_page_soup.find("div", {"class": "desc"}).text
        return resp

    def extract_all(self) -> dict[str, dict[str, t.Any]]:
        """Extract all possible contents from the page"""
        resp = {"headers": {}, "basics": {}, "casts": {}, "reviews": {}}
        resp["headers"] = self.extract_headers()
        resp["basics"] = self.extract_basics()
        resp["casts"] = self.extract_casts()
        resp["reviews"] = self.extract_reviews()
        resp["others"] = self.extract_others()
        return resp

    def __call__(self):
        """Extract all possible contents from the page"""
        return self.extract_all()


class BaseMovieDetailsExtractor(BaseDetailsExtractor):
    """`Movie` details extractor"""


class TVSeriesDetailsExtractor(BaseDetailsExtractor):
    """`TV Series` details extractor"""
