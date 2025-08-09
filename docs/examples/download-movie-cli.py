from moviebox_api.cli import Downloader


async def main():
    downloader = Downloader()
    movie_path, subtitle_path = await downloader.download_movie("avatar")
    print(movie_path, subtitle_path, sep="\n")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
