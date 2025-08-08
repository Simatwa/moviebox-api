from tests import project_dir

content_names = ["content_path"]
content_paths = (
    [project_dir / "assets/recons/movies.0/titanic-page-details-pretty.html"],
    [project_dir / "assets/recons/series/merlin-page-details-pretty.html"],
)


def read_content(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()
