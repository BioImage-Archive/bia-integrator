"""Test core functions of script to map image related artefacts to 2025/04 version of models"""

import os
from pathlib import Path
import pytest
from bia_shared_datamodels import bia_data_model, semantic_models

# Modify python path to allow importing script functions
mapping_script_path = str(Path(__file__).parents[1] / "scripts")
python_path = os.environ.get("PYTHONPATH", "")
os.environ["PYTHONPATH"] = ";".join(
    [
        mapping_script_path,
        python_path,
    ]
)
from scripts.map_image_related_artefacts_to_2025_04_models import (
    map_image_representation_to_2025_04_model,
)

accession_id = "S-BIAD-MAP-TO-2025-04-MODELS-TEST"


@pytest.fixture
def pre_2025_04_image_representation_dict() -> dict:
    return {
        "uuid": "570a177d-de5d-4bee-bbd1-fd2dcbec9e2a",
        "representation_of_uuid": "e7322131-8e27-455d-b9fc-8add0719af70",
        "use_type": "INTERACTIVE_DISPLAY",
        "image_format": ".ome.zarr",
        "attribute": [],
        "total_size_in_bytes": 0,
        "version": 0,
        "file_uri": [
            "https://uks3/testbucket-bia/S-BIAD-MAP-TO-2025-04-MODELS-TEST/image_uuid/image_representation_uuid.ome.zarr",
        ],
        "physical_size_x": 1,
        "physical_size_y": 1,
        "physical_size_z": 1,
        "size_x": 1,
        "size_y": 1,
        "size_z": 1,
        "size_c": 1,
        "size_t": 1,
        "image_viewer_setting": [],
        "model": {"type_name": "ImageRepresentation", "version": 3},
    }


@pytest.fixture
def expected_2025_04_image_representation(
    expected_2025_04_image,
) -> bia_data_model.ImageRepresentation:
    image_representation_dict = {
        "uuid": "8d225268-d47b-4512-8cf3-0ba14a8be541",
        "representation_of_uuid": str(expected_2025_04_image.uuid),
        "use_type": "INTERACTIVE_DISPLAY",
        "image_format": ".ome.zarr",
        "total_size_in_bytes": 0,
        "version": 0,
        "object_creator": semantic_models.Provenance.bia_image_conversion,
        "file_uri": [
            "https://uks3/testbucket-bia/S-BIAD-MAP-TO-2025-04-MODELS-TEST/image_uuid/image_representation_uuid.ome.zarr",
        ],
        "voxel_physical_size_x": 1,
        "voxel_physical_size_y": 1,
        "voxel_physical_size_z": 1,
        "size_x": 1,
        "size_y": 1,
        "size_z": 1,
        "size_c": 1,
        "size_t": 1,
        "image_viewer_setting": [],
        # TODO: confirm with FS if "version" here should be 4
        "model": {"type_name": "ImageRepresentation", "version": 3},
        "additional_metadata": [
            {
                "provenance": semantic_models.Provenance.bia_ingest,
                "name": "uuid_unique_input",
                # using str(use_type)+image_format as unique string
                "value": {"uuid_unique_input": "INTERACTIVE_DISPLAY.ome.zarr"},
            }
        ],
    }
    return bia_data_model.ImageRepresentation.model_validate(image_representation_dict)


@pytest.fixture
def expected_2025_04_image() -> bia_data_model.Image:
    # TODO: Compute proper uuids (i.e. based on actual study_uuid for file reference, creation process and dataset)
    image_dict = {
        "uuid": "b3f9004c-8c9a-4344-bffc-cab4bcf52a10",
        "version": 0,
        "model": {"type_name": "Image", "version": 1},
        "additional_metadata": [
            {
                "provenance": semantic_models.Provenance.bia_image_assignment,
                "name": "attributes_from_file_reference_0797dc78-5993-4add-b0fc-235c52055b97",
                "value": {
                    "attributes": [
                        "3d_multichannel_time_series/image_01_channel_00_slice_001_time0000.tiff"
                    ]
                },
            },
            {
                "provenance": semantic_models.Provenance.bia_ingest,
                "name": "uuid_unique_input",
                # using "".join(original_file_reference_uuid) as unique string
                "value": {"uuid_unique_input": "0797dc78-5993-4add-b0fc-235c52055b97"},
            },
        ],
        "original_file_reference_uuid": [
            "0797dc78-5993-4add-b0fc-235c52055b97",
        ],
        "creation_process_uuid": "b5d98aa9-79ce-4106-90b2-d3687eac67f0",
        "submission_dataset_uuid": "ae32e92d-84f9-4119-82d1-70cb36477bc0",
        "object_creator": semantic_models.Provenance.bia_image_assignment,
    }
    return bia_data_model.Image.model_validate(image_dict)


def test_map_image_representation(
    pre_2025_04_image_representation_dict,
    expected_2025_04_image_representation,
    expected_2025_04_image,
):
    mapped_image_representation = map_image_representation_to_2025_04_model(
        pre_2025_04_image_representation_dict, str(expected_2025_04_image.uuid)
    )
    assert mapped_image_representation == expected_2025_04_image_representation
