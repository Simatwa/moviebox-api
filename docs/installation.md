## Installing from Pypi

We shall be using [uv tool](https://docs.astral.sh/uv/)

### With required dependencies

=== "Install"

    ```sh
    uv pip install moviebox-api
    ```

=== "Add to project"

    ```sh
    uv add moviebox-api
    ```
### With [commandline](./v1/cli.md) extra dependencies

=== "Install"

    ```sh
    uv pip install "moviebox-api[cli]"
    ```

=== "Add to project"

    ```sh
    uv add "moviebox-api[cli]"
    ```

!!! important "CLI utils"
    At some point developers would want to make use of CLI utility functions for operations such as prompting users to choosing movie quality to be processed etc. This will require the commandline extra dependencies installed.

## Installing from source

If you like new features before actual releases:

=== "Install"

    ```sh
    uv pip install git+https://github.com/Simatwa/moviebox-api.git[cli]
    ```

=== "Add to project"

    ```sh
    uv add git+https://github.com/Simatwa/moviebox-api.git[cli]
    ```

???+ warning "Git required"
    For this method to work you need to have [git tool](https://git-scm.com) installed.


## Termux Installation (Android)

```sh
pip install moviebox-api --no-deps
pip install 'pydantic==2.9.2'
pip install rich click bs4 httpx throttlebuster
```