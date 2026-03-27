from tests import project_dir

content_names = ["content_path"]
content_paths = (
    [project_dir / "assets/data/avatar.page"],
    [project_dir / "assets/data/shannara-chronicles.page"],
)
# TODO: Update these contents in path regularly


def read_content(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()
