import pytest
from bia_integrator_api.models import Attribute
from bia_converter.utils import add_or_update_attribute

@pytest.fixture
def static_display_attribute1() -> Attribute:
    return Attribute.model_validate({
        "provenance": "bia_image_conversion",
        "name": "image_static_display_uri",
        "value": {
            "key1": {"uri": "file_uri1", "size": [512, 512],},
        },
    })

@pytest.fixture
def static_display_attribute2() -> Attribute:
    return Attribute.model_validate({
        "provenance": "bia_image_conversion",
        "name": "image_static_display_uri",
        "value": {
            "key2": {"uri": "file_uri2", "size": [512, 512],},
        },
    })

@pytest.fixture
def static_display_attribute1_updated() -> Attribute:
    return Attribute.model_validate({
        "provenance": "bia_image_conversion",
        "name": "image_static_display_uri",
        "value": {
            "key1": {"uri": "file_uri1_updated", "size": [512, 512],},
        },
    })

@pytest.fixture
def attribute1() -> Attribute:
    return Attribute.model_validate({
        "provenance": "bia_image_conversion",
        "name": "test case 1",
        "value": {
            "test case 1": "test case 1",
        }
    })

@pytest.fixture
def attribute1_updated() -> Attribute:
    return Attribute.model_validate({
        "provenance": "bia_image_conversion",
        "name": "test case 1",
        "value": {
            "test case 1": "test case 1 updated",
        }
    })

@pytest.fixture
def attribute2() -> Attribute:
    return Attribute.model_validate({
        "provenance": "bia_image_conversion",
        "name": "test case 2",
        "value": {
            "test case 2": "test case 2",
        }
    })

def test_add_new_attribute(attribute1, attribute2):
    attributes = [attribute1,]
    new_attr = attribute2

    add_or_update_attribute(new_attr, attributes)

    assert new_attr in attributes
    assert len(attributes) == 2


def test_update_existing_attribute(attribute1, attribute1_updated):
    attributes = [attribute1,]
    updated_attr = attribute1_updated

    add_or_update_attribute(updated_attr, attributes)

    assert attributes[0].value == attribute1_updated.value
    assert len(attributes) == 1

def test_update_existing_attribute_static_display_uri(static_display_attribute1, static_display_attribute1_updated):
    attributes = [static_display_attribute1,]
    updated_attr = static_display_attribute1_updated

    add_or_update_attribute(updated_attr, attributes)

    assert attributes[0].value == static_display_attribute1_updated.value
    assert len(attributes) == 1


def test_merge_image_static_display_uri(static_display_attribute1, static_display_attribute2):
    attributes = [static_display_attribute1]
    update_attr = static_display_attribute2

    add_or_update_attribute(update_attr, attributes)

    expected_value = {
        "key1": {"uri": "file_uri1", "size": [512, 512],},
        "key2": {"uri": "file_uri2", "size": [512, 512],},
    }
    assert attributes[0].value == expected_value
    assert len(attributes) == 1


def test_append_if_not_found(attribute1):
    attributes = []
    new_attr = attribute1

    add_or_update_attribute(new_attr, attributes)

    assert attributes == [new_attr]


def test_no_duplicate_addition(attribute1):
    attributes = [attribute1,]
    duplicate = attribute1

    add_or_update_attribute(duplicate, attributes)

    assert len(attributes) == 1
    assert attributes[0].value == attribute1.value