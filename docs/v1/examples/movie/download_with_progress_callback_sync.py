from moviebox_api.v1 import DownloadTracker, MovieAuto


def progress_callback(progress: DownloadTracker):
    percent = (progress.downloaded_size / progress.expected_size) * 100
    print(f"[{percent:.2f}%] Downloading {progress.saved_to.name}", end="\r")


def main():
    auto = MovieAuto(tasks=1)
    auto.run_sync("Avatar", progress_hook=progress_callback)


if __name__ == "__main__":
    main()
