Core movie operations includes the following in their order:

1. Searching for a particular movie
2. Fetching more details about it
3. Identifying urls pointing to different files in regard to video quality & subtitle language
4. Downloading selected movie file and subtitle file

## Movie Search

We can locate movies this way:

=== "Async"
    ```py { .annotate }
    --8<-- "v1/examples/search_movie.py"
    ```

    1. `#!python search_results.first_item` is shortcut for `search_results.items[0]`
    2. This is just whatever `.get_content()` returned passed over to a pydantic model

=== "Sync"
    ```py { .annotate }
    --8<-- "v1/examples/search_movie_sync.py"
    ```

    1. `#!python search_results.first_item` is shortcut for `search_results.items[0]`
    2. This is just whatever `.get_content()` returned passed over to a pydantic model

???+ tip "Developer experience"
    As you have seen from the above example, each of the core classes - `Search`, `MovieDetails`, `DownloadableMovieFilesDetail` - has the two methods ie. `get_content()` and `get_content_model()`. For the proceeding examples we shall be using `get_content_model()` method for benefits that comes from working with structured data such as type hints etc.

## Movie Details

There are two ways of going about this:

1. Using search results item
2. Using specific item page URL
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

    1. obtained from `!#python target_item.page_url`
    2. `<class 'moviebox_api.v1.extractor.models.json.ItemJsonDetailsModel'>`

=== "Sync"
    ```py { .annotate }
    --8<-- "v1/examples/movie_details_using_page_url_sync.py"
    ```

    1. obtained from `#!python target_item.page_url`
    2. `<class 'moviebox_api.v1.extractor.models.json.ItemJsonDetailsModel'>`

## Downloadable Movie Files Detail

For better understanding, take this as file metadata - files in this case being **movie file** and **subtitle file**.

These metadata include *file urls*, *file sizes*, *video quality* and *subtitle language*.

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