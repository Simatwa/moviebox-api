import logging

logging.basicConfig(
    format="[%(asctime)s] : %(levelname)s - %(message)s",
    datefmt="%d-%b-%Y %H:%M:%S",
    level=logging.INFO,
)

import json
from moviebox_api.requests import Session
from moviebox_api.core import Search
from moviebox_api.constants import SubjectType


async def main():
    session = Session()

    url = "https://moviebox.pk/detail/merlin-sMxCiIO6fZ9?id=8382755684005333552&scene&page_from=search_detail&type=%2Fmovie%2Fdetail"

    url = "https://moviebox.pk/detail/titanic-m7a9yt0abq6?id=5390197429792821032&scene&page_from=search_detail&type=%2Fmovie%2Fdetail"
    resp = await session.get_with_cookies(url)

    with open("titanic-page-details.html", "wb") as fh:
        fh.write(bytes(resp.text, "utf-8"))
    exit()

    search = Search(session, keyword="Titanic", subject_type=SubjectType.MOVIES)
    search_results = await search.get_content()
    with open("titanic-search.json", "w") as fh:
        json.dump(search_results, fh, indent=4)
    exit()
    target_search_results = search_results.first_item

    resp = session.get("")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
