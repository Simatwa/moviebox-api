import logging

logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%d-%b-%Y %H:%M:%S",
    level=logging.DEBUG,
)

from moviebox_api.requests import Session
import json


def dump_json_to(data: dict, filename: str):
    with open(filename, "w") as fh:
        json.dump(data, fh, indent=4)


async def main():
    session = Session()
    url = "https://moviebox.ng/wefeed-h5-bff/web/subject/play?subjectId=4006958073083480920&se=1&ep=1"
    data = await session.get_with_cookies(url=url)
    print(data)
    exit()
    dump_json_to(data, "play-series-episode.json")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
