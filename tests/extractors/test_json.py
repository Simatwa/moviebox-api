import pytest

from moviebox_api.extractor._core import JsonDetailsExtractor
from tests.extractors import (
    content_names,
    content_paths,
    read_content,
)


@pytest.mark.parametrize(content_names, content_paths)
def test_extract_whole_data(content_path):
    content = read_content(content_path)
    extractor = JsonDetailsExtractor(content)
    assert type(extractor.details) is dict
    assert type(extractor.data) is dict
    assert type(extractor.subject) is dict
    assert type(extractor.metadata) is dict
    assert type(extractor.resource) is dict
    assert type(extractor.reviews) is list
    assert type(extractor.seasons) is list
    assert type(extractor.stars) is list
    assert type(extractor.page_details) is dict
