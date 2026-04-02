## Background

This is the very first version of the API. Some parts of it **scrape data** from HTML-formatted pages, while others fetch data directly from the **REST API server**.

## Download Movie

This can be done in a very straightforward way:

=== "Async"

    ```py
    --8<-- "v1/examples/auto_movie.py"
    ```
=== "Sync"

    ```py
    --8<-- "v1/examples/auto_movie_sync.py"
    ```

Behind the scenes, this script does the following:

1. Performs a movie search
2. Presents the search results for the user to select one
3. Downloads both the movie and subtitle files

### Download with Progress Callback

=== "Async"

    ```py
    --8<-- "v1/examples/download_with_progress_callback.py"
    ```

=== "Sync"

    ```py
    --8<-- "v1/examples/download_with_progress_callback_sync.py"
    ```

!!! question "Why TV series lack **Auto**magic"
    This is a deliberate choice by the [developers](https://github.com/Simatwa). The current focus is more on implementing new features rather than adding miscellaneous ones. It may be implemented in the future, or you could **[submit a PR](https://github.com/Simatwa/moviebox-api/pulls)**.
