from pathlib import Path
import pytest
from unittest import mock
import json

from ome_types import from_xml

from scripts.extract_ome_metadata import get_image_metadata
from bia_integrator_core.models import BIAImage, BIAImageRepresentation

test_accession_id = "S-BIAD000"
test_image_uuid = "00000000-0000-0000-0000-000000000000"
test_image_rep_path = Path(__file__).resolve().parent.parent / f"resources/bia_integrator_data/{test_accession_id}/{test_image_uuid}/{test_image_uuid}.zarr/0"
test_image_rep_uri = r"file://" + f"{test_image_rep_path}"

content = (Path(test_image_rep_path).parent / "OME/METADATA.ome.xml").read_text()
actual_ome_metadata = from_xml(content, parser='lxml', validate=False)
expected_ome_metadata = json.loads(actual_ome_metadata.images[0].pixels.json())

def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self):
            self.status_code = 200
            self.content = (Path(test_image_rep_path).parent / "OME/METADATA.ome.xml").read_text()

        def json(self):
            return self.json_data

    return MockResponse()

@mock.patch("bia_integrator_core.models.requests.get", side_effect=mocked_requests_get)
def test_get_image_metadata(mock_get):
    """Test function to get image metadata"""
    
    test_image_rep = BIAImageRepresentation(
        accession_id=test_accession_id,
        image_id=test_image_uuid,
        size=0,
        type="ome_ngff",
        uri=test_image_rep_uri
    )
    test_image = BIAImage(
        id=test_image_uuid,
        original_relpath=test_image_rep_path,
        representations=[test_image_rep,]
    )
    ome_metadata = get_image_metadata(test_image)
    assert ome_metadata == expected_ome_metadata
