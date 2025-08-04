import pytest
from moviebox_api.extractor.movie import BaseMovieDetailsExtractor


content_names = ["content_path"]

content_paths = (
    ["recons/movies.0/titanic-page-details-pretty.html"],
    ["recons/movies.0/titanic-page-details.html"],
)


def read_content(path):
    with open(path) as fh:
        return fh.read()


@pytest.mark.parametrize(content_names, content_paths)
def test_extract_headers(content_path):
    content = read_content(content_path)
    extractor = BaseMovieDetailsExtractor(content)
    extracted_header_details = extractor.extract_headers()
    assert isinstance(extracted_header_details, dict)
    assert extracted_header_details.get("title") is not None


@pytest.mark.parametrize(content_names, content_paths)
def test_extract_basics(content_path):
    content = read_content(content_path)
    extractor = BaseMovieDetailsExtractor(content)
    extracted_details = extractor.extract_basics()
    assert isinstance(extracted_details, dict)
    assert extracted_details.get("title") is not None


@pytest.mark.parametrize(content_names, content_paths)
def test_extract_casts(content_path):
    content = read_content(content_path)
    extractor = BaseMovieDetailsExtractor(content)
    extracted_details = extractor.extract_casts()
    assert isinstance(extracted_details, dict)
    assert extracted_details.get("casts") is not None


@pytest.mark.parametrize(content_names, content_paths)
def test_extract_reviews(content_path):
    content = read_content(content_path)
    extractor = BaseMovieDetailsExtractor(content)
    extracted_details = extractor.extract_reviews()
    assert isinstance(extracted_details, dict)
    assert extracted_details.get("reviews") is not None


@pytest.mark.parametrize(content_names, content_paths)
def test_extract_others(content_path):
    content = read_content(content_path)
    extractor = BaseMovieDetailsExtractor(content)
    extracted_details = extractor.extract_others()
    assert isinstance(extracted_details, dict)
    assert extracted_details.get("tip") is not None


@pytest.mark.parametrize(content_names, content_paths)
def test_extract_all(content_path):
    content = read_content(content_path)
    extractor = BaseMovieDetailsExtractor(content)
    extracted_details = extractor.extract_all()
    assert isinstance(extracted_details, dict)
    assert extracted_details.get("basics") is not None
