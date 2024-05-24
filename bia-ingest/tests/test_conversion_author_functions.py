import json
import pytest
from bia_ingest.models import Author, Affiliation
from bia_ingest.biostudies import Submission
from bia_ingest.conversion import find_and_convert_authors


@pytest.fixture
def create_author():
    def _create_author(name, email, role, affiliation, orcid):
        author = Author(
            name=name,
            email=email,
            role=role,
            affiliation=Affiliation(name=affiliation),
            orcid=orcid,
        )
        return author

    return _create_author


def test_find_authors_in_submission(submission, create_author):
    expected_author1 = create_author(
        name="Test Author1",
        email="test_author1@ebi.ac.uk",
        role="corresponding author",
        affiliation="Test College 1",
        orcid="0000-0000-0000-0000",
    )
    expected_author2 = create_author(
        name="Test Author2",
        email="test_author2@ebi.ac.uk",
        role="first author",
        affiliation="Test College 2",
        orcid="1111-1111-1111-1111",
    )
    extracted_authors = find_and_convert_authors(submission)
    assert len(extracted_authors) == 2
    assert expected_author1 in extracted_authors
    assert expected_author2 in extracted_authors
