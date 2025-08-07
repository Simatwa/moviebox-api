from moviebox_api.cli.downloader import Downloader


async def main():
    downloader = Downloader()
    await downloader.download_movie("avatar")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
