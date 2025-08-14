from moviebox_api.cli import Downloader


async def main():
    downloader = Downloader()
    movie_details, subtitle_details = await downloader.download_movie("avatar")
    print(movie_details, subtitle_details, sep="\n")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
