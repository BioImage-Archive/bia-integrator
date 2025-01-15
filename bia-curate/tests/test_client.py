import pytest
from unittest.mock import MagicMock, patch
from bia_curate.client import store_object_in_api_idempotent, update_object_in_api_version_checked, update_attributes
from bia_integrator_api.models import BioSample, Attribute
from bia_integrator_api.exceptions import NotFoundException

@pytest.fixture
def mock_api_client():
    with patch('bia_curate.client.api_client') as mock_client:
        yield mock_client

def test_store_object_in_api_idempotent(mock_api_client):
    # Create a mock BioSample object
    bio_sample = BioSample(uuid="test-uuid", name="Test BioSample")

    # Mock the get function to raise NotFoundException
    mock_api_client.get_bio_sample.side_effect = NotFoundException

    # Call the function
    store_object_in_api_idempotent(bio_sample)

    # Assert that the post function was called
    mock_api_client.post_bio_sample.assert_called_once_with(bio_sample)

def test_store_object_in_api_idempotent_existing(mock_api_client):
    # Create a mock BioSample object
    bio_sample = BioSample(uuid="test-uuid", name="Test BioSample")

    # Mock the get function to return the existing object
    mock_api_client.get_bio_sample.return_value = bio_sample

    # Call the function
    store_object_in_api_idempotent(bio_sample)

    # Assert that the post function was not called
    mock_api_client.post_bio_sample.assert_not_called()

def test_update_object_in_api_version_checked(mock_api_client):
    # Create a mock BioSample object
    bio_sample = BioSample(uuid="test-uuid", name="Test BioSample")

    # Call the function
    update_object_in_api_version_checked(bio_sample)

    # Assert that the post function was called
    mock_api_client.post_bio_sample.assert_called_once_with(bio_sample)

def test_update_attributes():
    existing_attributes = [
        Attribute(name="attr1", value="value1"),
        Attribute(name="attr2", value="value2"),
    ]
    new_attributes = [
        Attribute(name="attr2", value="new_value2"),
        Attribute(name="attr3", value="value3"),
    ]

    updated_attributes = update_attributes(existing_attributes, new_attributes)

    assert len(updated_attributes) == 3
    assert updated_attributes[0].value == "value1"
    assert updated_attributes[1].value == "new_value2"
    assert updated_attributes[2].value == "value3"