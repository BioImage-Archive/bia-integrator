from bia_shared_datamodels.utils import sanitise_doi

import pytest

@pytest.mark.parametrize(
    ("doi", "expected_sanitised_doi"),
    (
        ("https://dx.doi.org/10.12345/test", "https://doi.org/10.12345/test"),
        ("https://doi.org/10.12345/test", "https://doi.org/10.12345/test"),
        ("http://dx.doi.org/10.12345/test", "https://doi.org/10.12345/test"),
        ("http://doi.org/10.12345/test", "https://doi.org/10.12345/test"),
        ("doi.org:10.12345/test", "https://doi.org/10.12345/test"),
        ("dx.doi.org:10.12345/test", "https://doi.org/10.12345/test"),
        ("doi.org/10.12345/test", "https://doi.org/10.12345/test"),
        ("dx.doi.org/10.12345/test", "https://doi.org/10.12345/test"),
        ("10.12345/test", "https://doi.org/10.12345/test"),
    ),
)
def test_dois_that_should_validate(doi, expected_sanitised_doi):
    assert(sanitise_doi(doi) == expected_sanitised_doi)

@pytest.mark.parametrize(
    "doi",
    (
        "https://d.doi.org/10.12345/test",
        "https://do.org/10.12345/test",
        "https://doi.org/1.12345/test",
        "https://doi.org/10.12/test",
        "https://doi.org/10.1234/",
        "doi.org:10.12345/",
        "d.doi.org:10.12345/test",
        "10.123/test",
    ),
)
def test_dois_that_should_not_validate(doi):
    with pytest.raises(ValueError):
        sanitise_doi(doi)

