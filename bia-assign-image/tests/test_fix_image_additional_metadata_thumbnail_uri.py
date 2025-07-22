"""Test functionality in script to fix thumbnail uris in image additional metadata"""

# We need to add the scripts folder to the python path
import sys
from pathlib import Path
import pytest

scripts_path = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, f"{scripts_path}")

from fix_additional_metadata import fix_thumbnail_uri


# Thumbnail test cases and expected result
@pytest.fixture
def thumbnail_from_migration_script() -> dict:
    return {
        "provenance": "bia_image_conversion",
        "name": "thumbnail_uri",
        "value": {
            "thumbnail_uri": [
                "http://thumbnail_uri",
            ]
        },
    }


@pytest.fixture
def thumbnail_from_convert() -> dict:
    return {
        "provenance": "bia_image_conversion",
        "name": "image_thumbnail_uri",
        "value": {"256x256 or 256_256": "http://thumbnail_uri", "size": (256, 256)},
    }


@pytest.fixture
def expected_thumbnail() -> dict:
    return {
        "provenance": "bia_image_conversion",
        "name": "image_thumbnail_uri",
        "value": {"256": {"size": 256, "uri": "http://thumbnail_uri"}},
    }


def test_fix_thumbnail_uri_from_migration_script(
    thumbnail_from_migration_script, expected_thumbnail
):
    fixed_thumbnail = fix_thumbnail_uri(thumbnail_from_migration_script)
    assert fixed_thumbnail == expected_thumbnail


def test_fix_wrong_thumbnail_details_from_convert(
    thumbnail_from_convert, expected_thumbnail
):
    fixed_thumbnail = fix_thumbnail_uri(thumbnail_from_convert)
    assert fixed_thumbnail == expected_thumbnail
