from moviebox_api.cli import Downloader


async def main():
    downloader = Downloader()
    episodes_content_map = await downloader.download_tv_series(
        "Merlin",
        season=1,
        episode=1,
        limit=1,
        # limit=13 # This will download entire 13 episodes of season 1
    )

    print(episodes_content_map)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
