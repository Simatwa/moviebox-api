Core movie operations include the following, in order:

1. Searching for a particular movie
2. Fetching more details about it
3. Identifying URLs pointing to different files with respect to video quality and subtitle language
4. Downloading the selected movie file and subtitle file

## Movie Search

We can locate movies this way:

=== "Async"

    ```py { .annotate }
    --8<-- "v1/examples/search_movie.py"
    ```

    1. `#!python search_results.first_item` is a shortcut for `search_results.items[0]`
    2. This is simply whatever `.get_content()` returns, passed into a Pydantic model

=== "Sync"

    ```py { .annotate }
    --8<-- "v1/examples/search_movie_sync.py"
    ```

    1. `#!python search_results.first_item` is a shortcut for `search_results.items[0]`
    2. This is simply whatever `.get_content()` returns, passed into a Pydantic model

???+ tip "Developer experience"
    As shown in the example above, each of the core classes — `Search`, `MovieDetails`, `DownloadableMovieFilesDetail` — has two methods, i.e., `get_content()` and `get_content_model()`. In the following examples, we will use the `get_content_model()` method due to the benefits of working with structured data such as type hints.

## Movie Details

There are two ways to approach this:

1. Using a search results item
2. Using a specific item page URL

*[URL]: From https://h5.aoneroom.com

### 1. Using Search Results Item

=== "Async"

    ```py title="movie_details_using_search_results_item.py" hl_lines="14-22"
    --8<-- "v1/examples/movie_details_using_search_results_item.py"
    ```

=== "Sync"

    ```py title="movie_details_using_search_results_item_sync.py" hl_lines="18-26"
    --8<-- "v1/examples/movie_details_using_search_results_item_sync.py"
    ```

### 2. Using Specific Item Page URL

=== "Async"

    ```py { .annotate }
    --8<-- "v1/examples/movie_details_using_page_url.py"
    ```

    1. Obtained from `#!python target_item.page_url`
    2. `<class 'moviebox_api.v1.extractor.models.json.ItemJsonDetailsModel'>`

=== "Sync"

    ```py { .annotate }
    --8<-- "v1/examples/movie_details_using_page_url_sync.py"
    ```

    1. Obtained from `#!python target_item.page_url`
    2. `<class 'moviebox_api.v1.extractor.models.json.ItemJsonDetailsModel'>`

## Downloadable Movie Files Detail

For better understanding, consider this as file metadata — where the files are the **movie file** and **subtitle file**.

These metadata include *file URLs*, *file sizes*, *video quality*, and *subtitle language*.

=== "Async"

    ```py hl_lines="25-36"
    --8<-- "v1/examples/downloadable_movie_file_details.py"
    ```

=== "Sync"

    ```py hl_lines="25-36"
    --8<-- "v1/examples/downloadable_movie_file_details_sync.py"
    ```

## Downloading Movie File

=== "Async"

    ```py hl_lines="26-34"
    --8<-- "v1/examples/download_movie_file.py"
    ```

=== "Sync"

    ```py hl_lines="26-34"
    --8<-- "v1/examples/download_movie_file_sync.py"
    ```

## Download Subtitle File

=== "Async"

    ```py hl_lines="28-37"
    --8<-- "v1/examples/download_subtitle_file.py"
    ```
=== "Sync"

    ```py hl_lines="28-37"
    --8<-- "v1/examples/download_subtitle_file_sync.py"
    ```
