import os
import pytest

@pytest.fixture(scope="session", autouse=True)
def set_env():
    os.environ["BIA_API_BASEPATH"] = "https://45.88.81.209:8080"
    os.environ["BIA_DISABLE_SSL_HOST_CHECK"] = "1"

@pytest.fixture(scope="session", autouse=True)
def accession_id():
    return "S-BIAD144"

@pytest.fixture
def expected_example_image_uri():
    return "https://uk1s3.embassy.ebi.ac.uk/bia-integrator-data/S-BIAD144/S-BIAD144-representative-512-512.png"

@pytest.fixture
def expected_release_date():
    return "2021-05-31"

@pytest.fixture
def expected_annotation_key():
    return "example_image_uri"


