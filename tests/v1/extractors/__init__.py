from moviebox_api.v1 import MovieDetails, Session, TVSeriesDetails
from tests.v1 import TEST_MOVIE_PAGE_URL, TEST_TV_SERIES_PAGE_URL, project_dir

content_names = ["content_path"]

MOVIE_CONTENT_PATH = project_dir / "assets/data/movie.page"
TV_SERIES_CONTENT_PATH = project_dir / "assets/data/tv_series.page"

content_paths = (
    [MOVIE_CONTENT_PATH],
    [TV_SERIES_CONTENT_PATH],
)


def read_content(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def write_content(path, content):
    with open(path, 'w') as fh:
        fh.write(content)


def update_movie_contents():
    session = Session()
    md = MovieDetails(TEST_MOVIE_PAGE_URL, session)

    content = md.get_html_content_sync()

    write_content(MOVIE_CONTENT_PATH, content)


def update_tv_series_contents():
    session = Session()
    md = TVSeriesDetails(TEST_TV_SERIES_PAGE_URL, session)

    content = md.get_html_content_sync()

    write_content(TV_SERIES_CONTENT_PATH, content)


update_movie_contents()
update_tv_series_contents()