from moviebox_api.v1 import MovieAuto


def main():
    auto = MovieAuto()
    movie_file, subtitle_file = auto.run_sync("Avatar")
    print(f"Movie: {movie_file.saved_to}")
    print(f"Subtitle: {subtitle_file.saved_to}")


if __name__ == "__main__":
    main()
