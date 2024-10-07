"""Test ImageRepresentation creation"""

from pathlib import Path
from typing import List

import bia_ingest.bia_object_creation_utils
from . import utils
import pytest
from bia_shared_datamodels import bia_data_model
from bia_ingest.persistence_strategy import DiskPersister
from bia_ingest.representation_creation import (
    image_representation,
)

experimentally_captured_image_uuid = utils.get_test_experimentally_captured_image()[
    0
].uuid
test_file_reference = utils.get_test_file_reference(
    ["file_list_study_component_1.json"]
)[0]

representation_location_base = (
    Path(__file__).parent / "data" / "test_image_representations" / "study_component1"
)
zarr_location = representation_location_base / "im06.ome.zarr"
zarr_total_size_in_bytes = (
    sum(f.stat().st_size for f in zarr_location.rglob("*"))
    + zarr_location.stat().st_size
)


@pytest.fixture()
def attributes_for_uuid() -> List[str]:
    return [
        "use_type",
        "original_file_reference_uuid",
        "representation_of_uuid",
    ]


@pytest.fixture()
def representation_dict_template() -> dict:
    return {
        "image_format": "",
        # "use_type": to be added during test,
        "file_uri": [],
        "original_file_reference_uuid": [test_file_reference.uuid],
        "representation_of_uuid": experimentally_captured_image_uuid,
        "total_size_in_bytes": 0,
        # "physical_size_x": 0,
        # "physical_size_y": 0,
        # "physical_size_z": 0,
        "size_x": None,
        "size_y": None,
        "size_z": None,
        "size_c": None,
        "size_t": None,
        "attribute": {},
        "version": 0,
    }


@pytest.mark.parametrize(
    (
        "representation_location",
        "representation_dict",
    ),
    (
        (
            f"{representation_location_base / 'im06.ome.zarr'}",
            {
                "use_type": "INTERACTIVE_DISPLAY",
            },
        ),
        (
            None,
            {
                "use_type": "UPLOADED_BY_SUBMITTER",
                "image_format": ".png",
                "total_size_in_bytes": 3,
                "file_uri": [
                    test_file_reference.uri,
                ],
            },
        ),
        (
            None,
            {
                "use_type": "INTERACTIVE_DISPLAY",
            },
        ),
        (
            None,
            {
                "use_type": "THUMBNAIL",
            },
        ),
    ),
)
def test_create_representation_of_single_image(
    representation_location,
    representation_dict,
    test_submission,
    result_summary,
    monkeypatch,
    attributes_for_uuid,
    representation_dict_template,
    tmp_path,
):
    disk_persister = DiskPersister(
        accession_id=test_submission.accno, output_dir_base=str(tmp_path)
    )
    model_dict = representation_dict_template | representation_dict
    model_dict["uuid"] = bia_ingest.bia_object_creation_utils.dict_to_uuid(
        model_dict, attributes_for_uuid
    )
    expected = bia_data_model.ImageRepresentation.model_validate(model_dict)

    test_file_reference_uuids = [
        test_file_reference.uuid,
    ]

    # Save file reference and eid required for test.
    disk_persister.persist(
        [
            test_file_reference,
        ]
    )
    disk_persister.persist(
        utils.get_test_experimental_imaging_dataset(),
    )

    # def mock_return_file_reference(input_path):
    #    input_path = str(input_path)
    #    if "file_reference" in input_path:
    #        return test_file_reference.model_dump_json()
    #    elif "experimental_imaging_dataset" in input_path:
    #        return utils.get_test_experimental_imaging_dataset()[0].model_dump_json()
    #    else:
    #        with open(input_path, "rt") as fid:
    #            text = "".join(fid.readlines())
    #        return text

    created = image_representation.create_image_representation(
        test_submission,
        test_file_reference_uuids,
        representation_use_type=representation_dict["use_type"],
        representation_location=representation_location,
        persister=disk_persister,
        result_summary=result_summary,
    )
    assert created == expected

    # Assert that correct artefacts were persisted to disk
    from_disk = disk_persister.fetch_by_uuid(
        [
            created.uuid,
        ],
        type(created),
    )[0]
    assert from_disk == expected

    # TODO: Need to assert experimentally captured image created and
    #       persisted correctly
