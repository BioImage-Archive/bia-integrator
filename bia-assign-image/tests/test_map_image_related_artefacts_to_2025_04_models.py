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
    map_image_to_2025_04_model,
)

accession_id = "S-BIAD-MAP-IMAGE-RELATED-ARTEFACTS-TO-2025-04-MODELS-TEST"


@pytest.fixture
def pre_2025_04_image_representation_dict() -> dict:
    model_dict = {
        "uuid": "570a177d-de5d-4bee-bbd1-fd2dcbec9e2a",
        "representation_of_uuid": "e7322131-8e27-455d-b9fc-8add0719af70",
        "use_type": "INTERACTIVE_DISPLAY",
        "image_format": ".ome.zarr",
        "attribute": [],
        "total_size_in_bytes": 0,
        "version": 0,
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
    file_uri = [
        f"https://uks3/testbucket-bia/{accession_id}/{model_dict['representation_of_uuid']}/{model_dict['uuid']}.ome.zarr",
    ]
    model_dict["file_uri"] = file_uri
    return model_dict


@pytest.fixture
def expected_2025_04_image_representation(
    pre_2025_04_image_representation_dict,
    expected_2025_04_image,
) -> bia_data_model.ImageRepresentation:
    image_representation_dict = {
        "uuid": "fee02b2d-2e5c-4994-9588-7763e8c26bee",
        "representation_of_uuid": str(expected_2025_04_image.uuid),
        "image_format": ".ome.zarr",
        "total_size_in_bytes": 0,
        "version": 0,
        "object_creator": semantic_models.Provenance.bia_image_conversion,
        "voxel_physical_size_x": 1,
        "voxel_physical_size_y": 1,
        "voxel_physical_size_z": 1,
        "size_x": 1,
        "size_y": 1,
        "size_z": 1,
        "size_c": 1,
        "size_t": 1,
        "image_viewer_setting": [],
        "model": {"type_name": "ImageRepresentation", "version": 4},
        "additional_metadata": [
            {
                "provenance": semantic_models.Provenance.bia_image_conversion,
                "name": "uuid_unique_input",
                "value": {
                    "uuid_unique_input": "{'conversion_function': 'map_image_representation_to_2025_04_model'}"
                },
            }
        ],
    }
    image_representation_dict["file_uri"] = pre_2025_04_image_representation_dict[
        "file_uri"
    ]
    return bia_data_model.ImageRepresentation.model_validate(image_representation_dict)


@pytest.fixture
def pre_2025_04_image_dict() -> dict:
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
    return image_dict


@pytest.fixture
def expected_2025_04_image() -> bia_data_model.Image:
    # image_dict = {
    #    "uuid": "b3f9004c-8c9a-4344-bffc-cab4bcf52a10",
    #    "version": 0,
    #    "model": {"type_name": "Image", "version": 2},
    #    "additional_metadata": [
    #        {
    #            "provenance": semantic_models.Provenance.bia_image_assignment,
    #            "name": "attributes_from_file_reference_0797dc78-5993-4add-b0fc-235c52055b97",
    #            "value": {
    #                "attributes": [
    #                    "3d_multichannel_time_series/image_01_channel_00_slice_001_time0000.tiff"
    #                ]
    #            },
    #        },
    #        {
    #            "provenance": semantic_models.Provenance.bia_ingest,
    #            "name": "uuid_unique_input",
    #            # using "".join(original_file_reference_uuid) as unique string
    #            "value": {"uuid_unique_input": "0797dc78-5993-4add-b0fc-235c52055b97"},
    #        },
    #    ],
    #    "original_file_reference_uuid": [
    #        "80ef897d-571f-401e-aeab-73c5da842c3b",
    #    ],
    #    "creation_process_uuid": "",
    #    "submission_dataset_uuid": "df381b39-0768-493e-90ed-7c653f012f1f",
    #    "object_creator": semantic_models.Provenance.bia_image_assignment,
    # }
    image_dict = {
        "object_creator": "bia_image_assignment",
        "uuid": "93de26f0-6d84-42a5-b6fc-fcd67a94f18e",
        "version": 0,
        "model": {"type_name": "Image", "version": 2},
        "additional_metadata": [
            {
                "provenance": "bia_image_assignment",
                "name": "attributes_from_file_reference_80ef897d-571f-401e-aeab-73c5da842c3b",
                "value": {"file_list_col1": "col1value", "file_list_col2": "col2value"},
            },
            {
                "provenance": "bia_image_assignment",
                "name": "file_pattern",
                "value": {
                    "file_pattern": "S-BIAD-MAP-IMAGE-RELATED-ARTEFACTS-TO-2025-04-MODELS-TEST/file_reference1.tif"
                },
            },
            {
                "provenance": "bia_image_assignment",
                "name": "uuid_unique_input",
                "value": {"uuid_unique_input": "80ef897d-571f-401e-aeab-73c5da842c3b"},
            },
        ],
        "submission_dataset_uuid": "df381b39-0768-493e-90ed-7c653f012f1f",
        "creation_process_uuid": "af26940e-35c7-470a-8037-0a27d45253b9",
        "original_file_reference_uuid": ["80ef897d-571f-401e-aeab-73c5da842c3b"],
    }
    return bia_data_model.Image.model_validate(image_dict)


def test_map_image_representation(
    pre_2025_04_image_representation_dict,
    expected_2025_04_image_representation,
    expected_2025_04_image,
):
    mapped_image_representation = map_image_representation_to_2025_04_model(
        pre_2025_04_image_representation_dict,
        str(expected_2025_04_image.uuid),
        accession_id,
    )
    assert mapped_image_representation == expected_2025_04_image_representation


# Test mapping UPLOADED_BY_SUBMITTER

# Test mapping THUMBNAIL AND STATIC_DISPLAY


def test_map_image(
    pre_2025_04_image_dict,
    expected_2025_04_image,
):
    mapped_image = map_image_to_2025_04_model(
        pre_2025_04_image_dict,
        accession_id,
        file_reference_uuids_2025_04=expected_2025_04_image.original_file_reference_uuid,
        dataset_uuid_2025_04=expected_2025_04_image.submission_dataset_uuid,
        api_target="local",
    )
    assert mapped_image == expected_2025_04_image


def test_update_mapped_image_from_pre_2025_04_representations_linking_image():
    pass
