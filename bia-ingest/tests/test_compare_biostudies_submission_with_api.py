import sys
from pathlib import Path
import json
from unittest.mock import Mock, MagicMock
from tempfile import TemporaryDirectory

from bia_integrator_api.models import BIAStudy
from bia_ingest.visitor import Visitor

script_path = Path(__file__).parent.parent / "scripts"
sys.path.append(f"{script_path}")
from compare_biostudies_and_api_submission import (
    compare_biostudies_with_api,
    requests,
    rw_client,
    main as main_func,
)

accession_id = "S-BIAD0001"
from_biostudies_str = """
    {
      "accno" : "S-BIAD0001",
      "title" : "Test Submission",
      "attributes" : [ {
        "name" : "Template",
        "value" : "BioImages.v4"
      }, {
        "name" : "ReleaseDate",
        "value" : "2024-02-21"
      }, {
        "name" : "AttachTo",
        "value" : "BioImages"
      } ],
      "type" : "submission"
    }
"""
from_biostudies = json.loads(from_biostudies_str)

expected_study_dict = {
    "attributes": {},
    "annotations_applied": True,
    "annotations": [],
    "context": "https://raw.githubusercontent.com/context.jsonld",
    "uuid": "ec7d5967-cbc0-4577-b602-c45c261e3597",
    "version": 1,
    "model": {"type_name": "BIAStudy", "version": 1},
    "title": "Test Submission",
    "description": "Test description.",
    "authors": [{"name": "Image Data Resource (IDR)"}],
    "organism": "Homo sapiens (human)",
    "release_date": "2024-02-21",
    "accession_id": "S-BIAD0001",
    "imaging_type": "imaging mass cytometry",
    "example_image_uri": "",
    "example_image_annotation_uri": "",
    "tags": [],
    "file_references_count": 3,
    "images_count": 0,
}

expected_study_api_model = BIAStudy(**expected_study_dict)

expected_comparison_result = {
    "mapped": [
        "From API .accession_id mapped to .submission.accno",
        "From API .title mapped to .submission.title",
        "From API .release_date mapped to .submission.attributes[1].name=ReleaseDate",
    ],
    "not_mapped": [
        ".submission.attributes[0].name=Template",
        ".submission.attributes[2].name=AttachTo",
        ".submission.type",
    ],
}

visitor = Visitor(accession_id)
visitor.visit("", from_biostudies)
flattened_contents_biostudies = visitor.flattened_contents_dict

visitor.reset(accession_id)
visitor.visit("", expected_study_dict)
flattened_contents_api = visitor.flattened_contents_dict


def setup_module(module):

    # Mock return values of rw_client
    rw_client.get_study = MagicMock(return_value=expected_study_api_model)

    mock_object_info = Mock(uuid=expected_study_api_model.uuid)
    rw_client.get_object_info_by_accession = MagicMock(return_value=[mock_object_info,])

    rw_client.get_study_images = MagicMock(return_value=[])
    rw_client.get_study_file_references = MagicMock(return_value=[])

    # Patch requests to return expected biostudies json
    mock_json_from_biostudies = Mock()
    mock_json_from_biostudies.json = MagicMock(return_value=from_biostudies)
    requests.get = MagicMock(return_value=mock_json_from_biostudies)


def test_compare_biostudies_with_api_function():

    comparison_result = compare_biostudies_with_api(
        flattened_contents_biostudies, flattened_contents_api
    )

    assert len(comparison_result) == 2
    assert comparison_result["mapped"] == expected_comparison_result["mapped"]
    assert comparison_result["not_mapped"] == expected_comparison_result["not_mapped"]


def test_compare_biostudies_and_api_main_function():

    with TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "comparison-result.json"
        assert not output_path.is_file()
        main_func(accession_id, str(output_path))
        assert output_path.is_file()

        comparison_result = json.loads(output_path.read_text())
        assert comparison_result == expected_comparison_result
