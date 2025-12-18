import pytest
from pydantic import BaseModel

from moviebox_api.extractor._core import (
    JsonDetailsExtractorModel,
    TagDetailsExtractorModel,
)
from tests.extractors import (
    content_names,
    content_paths,
    read_content,
)


@pytest.mark.parametrize(content_names, content_paths)
def test_json_details_extractor_model(content_path):
    content = read_content(content_path)
    extractor = JsonDetailsExtractorModel(content)
    assert isinstance(extractor.details, BaseModel)
    assert isinstance(extractor.data, BaseModel)
    assert isinstance(extractor.subject, BaseModel)
    assert isinstance(extractor.metadata, BaseModel)

    assert isinstance(extractor.resource, BaseModel)
    assert isinstance(extractor.reviews[0], BaseModel)
    assert isinstance(extractor.seasons[0], BaseModel)

    assert isinstance(extractor.stars[0], BaseModel)
    assert isinstance(extractor.page_details, BaseModel)


@pytest.mark.parametrize(content_names, content_paths)
def test_tag_details_extractor_model(content_path):
    content = read_content(content_path)
    extractor = TagDetailsExtractorModel(content)
    assert isinstance(extractor.extract_headers(), BaseModel)
    assert isinstance(extractor.extract_basics(), BaseModel)
    assert isinstance(extractor.extract_casts()[0], BaseModel)

    assert isinstance(extractor.extract_reviews()[0], BaseModel)
    assert isinstance(extractor.extract_others(), BaseModel)
