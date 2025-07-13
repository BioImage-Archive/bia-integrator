"""Test functionality in script to fix uris of static images in image additional metadata"""

# We need to add the scripts folder to the python path
import sys
from pathlib import Path
import pytest

scripts_path = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, f"{scripts_path}")

from fix_additional_metadata import fix_static_display_uri


# Static display test cases and expected result
@pytest.fixture
def static_display_from_migration_script() -> dict:
    return {
        "provenance": "bia_image_conversion",
        "name": "static_display_uri",
        "value": {
            "static_display_uri": [
                "http://static_display_uri",
            ]
        },
    }


@pytest.fixture
def static_display_from_convert_v1() -> dict:
    return {
        "provenance": "bia_image_conversion",
        "name": "image_static_display_uri",
        "value": {"slice": "http://static_display_uri", "size": (256, 256)},
    }


@pytest.fixture
def expected_static_display() -> dict:
    return {
        "provenance": "bia_image_conversion",
        "name": "image_static_display_uri",
        "value": {
            "slice": {
                "uri": "http://static_display_uri",
                "size": 512,
            }
        },
    }


def test_fix_static_display_uri_from_migration_script(
    static_display_from_migration_script, expected_static_display
):
    fixed_static_display = fix_static_display_uri(static_display_from_migration_script)
    assert fixed_static_display == expected_static_display


def test_fix_wrong_static_display_details_from_convert(
    static_display_from_convert, expected_static_display
):
    fixed_static_display = fix_static_display_uri(static_display_from_convert)
    assert fixed_static_display == expected_static_display
