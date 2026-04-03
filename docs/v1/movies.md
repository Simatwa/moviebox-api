## Overview 

Core movie operations include the following, in order:

1. Searching for a particular movie
2. Fetching more details about it
3. Identifying URLs pointing to different files with respect to video quality and subtitle language
4. Downloading the selected movie file and subtitle file

## Movie Search

We can locate movies this way:

=== "Async"

    ```py { .annotate }
    --8<-- "v1/examples/movie/search_movie.py"
    ```

    1. Output: `#!python <class 'dict'>`. Access list of movies matching the query from `#!python search_results['items']`
    2. This is simply whatever `.get_content()` returns, passed into a Pydantic model
    3. Output: `#!python  <class 'moviebox_api.v1.models.SearchResultsModel'>`. Access search result items from `#!python search_results.items`

=== "Sync"

    ```py { .annotate }
    --8<-- "v1/examples/movie/search_movie_sync.py"
    ```

    1. Output: `#!python <class 'dict'>`. Access list of movies matching the query from `#!python search_results['items']`
    2. This is simply whatever `.get_content()` returns, passed into a Pydantic model
    3. Output: `#!python  <class 'moviebox_api.v1.models.SearchResultsModel'>`. Access search result items from `#!python search_results.items`

???+ tip "Developer experience"
    As shown in the example above, each of the core classes — `Search`, `MovieDetails`, `DownloadableMovieFilesDetail` — has two methods, i.e., `get_content()` and `get_content_model()`. In the following examples, we will use the `get_content_model()` method due to the benefits of working with structured data such as type hints.

### Navigating Search Results Page

#### Next Page

```py { .annotate }
async def search_movie():
    ...
    contents: SearchResultsModel = await search.get_content_model() # (3)

    next_search: Search = search.next_page(search_results)  # (1)

    next_contents: SearchResultsModel = await next_search.get_content_model()  # (2)
```

1. Page 2 search instance
2. Page 2 search results
3. Page 1 search results

#### Previous Page

```py { .annotate }
async def search_movie():
    search = Search(Session(), query="avatar" page=3, per_page=5)

    contents:  SearchResultsModel = await search.get_content_model()  # (1)

    previous_search: Search = search.previous_page(contents)  # (2)

    previous_contents:  SearchResultsModel = await previous_search.get_content_model()  # (3)
```

1. Page 3 search results
2. Page 2 search instance
3. Page 2 search results

???+ tip "Navigation Check"
    Before navigating to next page, it's better to consider `#!python search_results.pager.hasMore` flag.

## Movie Details

There are two ways to approach this:

1. Using a search results item
2. Using a specific item page URL

*[URL]: From https://h5.aoneroom.com

### 1. Using Search Results Item

=== "Async"

    ```py title="movie_details_using_search_results_item.py" hl_lines="14-22"
    --8<-- "v1/examples/movie/movie_details_using_search_results_item.py"
    ```

    1. Shortcut for `#!python search_results.items[0]`
    2. Output: `#!python <class 'moviebox_api.v1.extractor.models.json.ItemJsonDetailsModel'>`

=== "Sync"

    ```py title="movie_details_using_search_results_item_sync.py" hl_lines="18-26"
    --8<-- "v1/examples/movie/movie_details_using_search_results_item_sync.py"
    ```

    1. Shortcut for `#!python search_results.items[0]`
    2. Output: `#!python <class 'moviebox_api.v1.extractor.models.json.ItemJsonDetailsModel'>`

### 2. Using Specific Item Page URL

=== "Async"

    ```py { .annotate }
    --8<-- "v1/examples/movie/movie_details_using_page_url.py"
    ```

    1. Obtained from `#!python target_item.page_url`
    2. `<class 'moviebox_api.v1.extractor.models.json.ItemJsonDetailsModel'>`

=== "Sync"

    ```py { .annotate }
    --8<-- "v1/examples/movie/movie_details_using_page_url_sync.py"
    ```

    1. Obtained from `#!python target_item.page_url`
    2. `<class 'moviebox_api.v1.extractor.models.json.ItemJsonDetailsModel'>`

## Downloadable Files Detail

For better understanding, consider this as file metadata — where the files are the **movie file** and **subtitle file**.

These metadata include *file URLs*, *file sizes*, *video quality*, and *subtitle language*.

=== "Async"

    ```py hl_lines="25-34"
    --8<-- "v1/examples/movie/downloadable_movie_file_details.py"
    ```

    1. !!! tip "Alternative"
        `#!python target_movie_details_instance = search.get_item_details(target_movie)`
    2. Output : `#!python  <class 'moviebox_api.v1.models.DownloadableFilesMetadata'>`

=== "Sync"

    ```py hl_lines="25-34"
    --8<-- "v1/examples/movie/downloadable_movie_file_details_sync.py"
    ```

## Downloading Movie File

=== "Async"

    ```py hl_lines="26-34"
    --8<-- "v1/examples/movie/download_movie_file.py"
    ```

=== "Sync"

    ```py hl_lines="26-34"
    --8<-- "v1/examples/movie/download_movie_file_sync.py"
    ```

## Download Subtitle File

=== "Async"

    ```py hl_lines="28-37"
    --8<-- "v1/examples/movie/download_subtitle_file.py"
    ```
=== "Sync"

    ```py hl_lines="28-37"
    --8<-- "v1/examples/movie/download_subtitle_file_sync.py"
    ```
