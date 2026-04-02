## Background

This is the very first version of the API. Some parts of it **scrape data** off html formatted pages while others fetch them directly from **REST-API server**

## Download Movie

This can be done very straightforward way:

=== "Async"

    ```py
    --8<-- "v1/examples/auto_movie.py"
    ```

=== "Sync"

    ```py
    --8<-- "v1/examples/auto_movie_sync.py"
    ```

Behind the hood this script does the following:

1. Performs movie search
2. Present the search results for user to select one
3. Download both movie and subtile files

### Download with Progress Callback

=== "Async"

    ```py
    --8<-- "v1/examples/download_with_progress_callback.py"
    ```

=== "Sync"

    ```py
    --8<-- "v1/examples/download_with_progress_callback_sync.py"
    ```


!!! question "Why TV-series lack **Auto**magic"
    It's by [developers](https://github.com/Simatwa) choice to be so. The focus is now channeled more towards implementing new features rather than adding miscellaneous ones. Perhaps it will be implemented someday, or could you **[submit a PR](https://github.com/Simatwa/moviebox-api/pulls)**?