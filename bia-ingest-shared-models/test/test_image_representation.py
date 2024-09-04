"""Test ImageRepresentation creation"""

from pathlib import Path
from . import utils
from bia_shared_datamodels import bia_data_model
from bia_ingest_sm.conversion import (
    image_representation,
)
from bia_ingest_sm.image_utils import image_utils

experimentally_captured_image_uuid = utils.get_test_experimentally_captured_image()[
    0
].uuid
test_file_reference = utils.get_test_file_reference(
    ["file_list_study_component_1.json"]
)[0]
# test_zarr_location = f"file://{Path(__file__).parent / 'data' / 'test_image_representations' / 'study_component1' / 'im06.zarr'}"
test_zarr_location = f"{Path(__file__).parent / 'data' / 'test_image_representations' / 'study_component1' / 'im06.zarr'}"


def test_get_create_zarr_representation_of_single_image(
    test_submission, result_summary, monkeypatch
):
    model_dict = {
        "image_format": "",
        "file_uri": [
            test_file_reference.uri,
        ],
        "original_file_reference_uuid": [test_file_reference.uuid],
        "representation_of_uuid": experimentally_captured_image_uuid,
        "total_size_in_bytes": 60360,
        # "physical_size_x": 0,
        # "physical_size_y": 0,
        # "physical_size_z": 0,
        "size_x": 100,
        "size_y": 80,
        "size_z": 1,
        "size_c": 3,
        "size_t": 1,
        "attribute": {},
        "version": 1,
    }
    model_dict["uuid"] = utils.dict_to_uuid(model_dict, list(model_dict.keys()))
    expected = bia_data_model.ImageRepresentation.model_validate(model_dict)

    test_file_reference_uuids = [
        test_file_reference.uuid,
    ]

    def mock_return_file_reference(input_path):
        input_path = str(input_path)
        if "file_reference" in input_path:
            return test_file_reference.model_dump_json()
        elif "experimental_imaging_dataset" in input_path:
            return utils.get_test_experimental_imaging_dataset()[0].model_dump_json()
        else:
            with open(input_path, "rt") as fid:
                text = "".join(fid.readlines())
            return text

    monkeypatch.setattr(image_utils.Path, "read_text", mock_return_file_reference)

    created = image_representation.image_representation_from_zarr(
        test_submission,
        test_file_reference_uuids,
        zarr_location=test_zarr_location,
        result_summary=result_summary,
    )
    assert created == expected
