from moviebox_api.v1 import MovieAuto


async def main():
    auto = MovieAuto()
    movie_file, subtitle_file = await auto.run("Avatar")
    print(f"Movie: {movie_file.saved_to}")
    print(f"Subtitle: {subtitle_file.saved_to}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
