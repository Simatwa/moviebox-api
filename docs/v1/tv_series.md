TV-Series operations follow the [same steps](./movies.md#overview){ data-preview } as those of movies, with the slight difference being the consideration of season and episode numbers, from the extraction of specific item details all the way to initiating the download process.

## Series Search

The only thing that changes from [movies search](./movies.md#movie-search){ data-preview } is the `subject_type` value:

=== "Async"
    ```py { .annotate }
    --8<-- "v1/examples/tv_series/search_tv_series.py"
    ```

    1. `#!python <class 'dict'>` access individual search result items from `#!python search_results["items"]`
    2. `#!python <class 'moviebox_api.v1.models.SearchResultsModel'>` access individual search result items from `#!python search_results.items`

=== "Sync"
    ```py { .annotate }
    --8<-- "v1/examples/tv_series/search_tv_series_sync.py"
    ```

    1. `#!python <class 'dict'>` access individual search result items from `search_results["items"]`
    2. `#!python <class 'moviebox_api.v1.models.SearchResultsModel'>` access individual search result items from `#!python search_results.items`

??? note "Search Results Navigation"
    It uses the same approach as [movies navigation](./movies.md#navigating-search-results-page){ data-preview }.

## TV-Series Details

This involves exploring a particular TV series and getting more information such as the number of episodes per season, available video resolutions, casts, etc.

There are 2 ways of going about this, just like in [movies](./movies.md#movie-details){ data-preview }:

### 1. Using Search Results Item

=== "Async"
    ```py hl_lines="17-26"
    --8<-- "v1/examples/tv_series/tv_series_details_using_search_results_item.py"
    ```

    1. Shortcut for `#!python search_results.items[0]`
    2. Output: `#!python <class 'moviebox_api.v1.extractor.models.json.ItemJsonDetailsModel'>`

=== "Sync"
    ```py hl_lines="17-26"
    --8<-- "v1/examples/tv_series/tv_series_details_using_search_results_item_sync.py"
    ```

    1. Shortcut for `#!python search_results.items[0]`
    2. Output: `#!python <class 'moviebox_api.v1.extractor.models.json.ItemJsonDetailsModel'>`

### 2. Using Item Page URL

The page URL is obtained from `#!python target_item.page_url`.

=== "Async"
    ```py { .annotate }
    --8<-- "v1/examples/tv_series/tv_series_details_using_item_page_url.py"
    ```

    1. Output: `#!python <class 'moviebox_api.v1.extractor.models.json.ItemJsonDetailsModel'>`
    2. The URL is obtained from `#!python target_item.page_url`. It makes more sense when loaded from cache.

=== "Sync"
    ```py { .annotate }
    --8<-- "v1/examples/tv_series/tv_series_details_using_item_page_url_sync.py"
    ```

    1. Output: `#!python <class 'moviebox_api.v1.extractor.models.json.ItemJsonDetailsModel'>`
    2. The URL is obtained from `#!python target_item.page_url`. It makes more sense when loaded from cache.

## Downloadable Files Detail

This follows the same principles as outlined in [movies](./movies.md#downloadable-files-detail){ data-preview }.

=== "Async"
    ```py hl_lines="22-35"
    --8<-- "v1/examples/tv_series/downloadable_files_details.py"
    ```

    1. Output: `#!python <class 'moviebox_api.v1.models.DownloadableFilesMetadata'>`

=== "Sync"
    ```py hl_lines="22-35"
    --8<-- "v1/examples/tv_series/downloadable_files_details_sync.py"
    ```

    1. Output: `#!python <class 'moviebox_api.v1.models.DownloadableFilesMetadata'>`

## Download Files

These are video and subtitle files.

### Download Video

=== "Async"
    ```py hl_lines="30-38"
    --8<-- "v1/examples/tv_series/download_video_file.py"
    ```

    1. Shortcut for `#!python downloadable_files_detail.downloads[0]`

=== "Sync"
    ```py hl_lines="30-38"
    --8<-- "v1/examples/tv_series/download_video_file_sync.py"
    ```

    1. Shortcut for `#!python downloadable_files_detail.downloads[0]`

### Download Subtitle

=== "Async"
    ```py hl_lines="30-38"
    --8<-- "v1/examples/tv_series/download_subtitle_file.py"
    ```

=== "Sync"
    ```py hl_lines="30-38"
    --8<-- "v1/examples/tv_series/download_subtitle_file_sync.py"
    ```