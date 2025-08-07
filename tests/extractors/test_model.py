import pytest

from tests.extractors import content_names, content_paths, read_content
from moviebox_api.extractor._core import JsonDetailsExtractorModel


def read_content(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


@pytest.mark.parametrize(content_names, content_paths)
def test_extract_whole_data(content_path):
    content = read_content(content_path)
    extractor = JsonDetailsExtractorModel(content)
    assert extractor.details is not None
    assert extractor.data is not None
    assert extractor.subject is not None
    assert extractor.metadata is not None
    assert extractor.resource is not None
    assert extractor.reviews is not None
    assert extractor.seasons is not None
    assert extractor.stars is not None
    assert extractor.page_details is not None
