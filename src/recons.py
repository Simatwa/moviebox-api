import logging

logging.basicConfig(
    format="[%(asctime)s] : %(levelname)s - %(message)s",
    datefmt="%d-%b-%Y %H:%M:%S",
    level=logging.INFO,
)


from moviebox_api import Auto

async def main():
    auto = Auto()
    movie_saved_to, subtitle_saved_to = await auto.run("Avatar",quality = "WORST")
    print(movie_saved_to, subtitle_saved_to, sep="\n", )
    # Output
    # /home/smartwa/.../Avatar - 1080P.mp4
    # /home/smartwa/.../Avatar - English.srt

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
