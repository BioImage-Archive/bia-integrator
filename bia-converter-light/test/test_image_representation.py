"""Test ImageRepresentation creation"""

from pathlib import Path
from typing import List
import uuid

import bia_ingest.bia_object_creation_utils
import pytest
from bia_shared_datamodels import bia_data_model, mock_objects
from bia_ingest.persistence_strategy import DiskPersister
from bia_ingest.bia_object_creation_utils import dict_to_uuid
from bia_converter_light import image_representation


@pytest.fixture()
def test_file_reference() -> bia_data_model.FileReference:
    """Return FileReference object to be used for test"""

    return bia_data_model.FileReference.model_validate(
        mock_objects.get_file_reference_dict(mock_objects.Completeness.COMPLETE)
    )


representation_location_base = (
    Path(__file__).parent / "data" / "test_image_representations" / "study_component1"
)
zarr_location = representation_location_base / "im06.ome.zarr"
zarr_total_size_in_bytes = (
    sum(f.stat().st_size for f in zarr_location.rglob("*"))
    + zarr_location.stat().st_size
)


@pytest.fixture()
def test_experimental_imaging_dataset(
    test_file_reference,
) -> bia_data_model.ExperimentalImagingDataset:
    """Return the test experimental imaging dataset to be used"""
    experimental_imaging_dataset_dict = (
        mock_objects.get_experimental_imaging_dataset_dict(
            mock_objects.Completeness.COMPLETE
        )
    )
    # Make the eid uuid correspond to that of the file reference as the
    # file reference version is used to get the eid during image creation
    experimental_imaging_dataset_dict["uuid"] = (
        test_file_reference.submission_dataset_uuid
    )
    experimental_imaging_dataset = (
        bia_data_model.ExperimentalImagingDataset.model_validate(
            experimental_imaging_dataset_dict
        )
    )

    # Populate attribute keys for uuids needed for creation of ECI
    experimental_imaging_dataset.attribute["subject_uuid"] = uuid.uuid4()
    experimental_imaging_dataset.attribute["acquisition_process_uuid"] = [
        uuid.uuid4(),
    ]

    return experimental_imaging_dataset


@pytest.fixture()
def test_experimentally_captured_image(
    test_file_reference, test_experimental_imaging_dataset
) -> bia_data_model.ExperimentallyCapturedImage:
    """Return test ExperimentallyCapturedImage"""
    model_dict = {
        "path": test_file_reference.file_path,
        "acquisition_process_uuid": [
            str(a)
            for a in test_experimental_imaging_dataset.attribute[
                "acquisition_process_uuid"
            ]
        ],
        "submission_dataset_uuid": str(test_experimental_imaging_dataset.uuid),
        "subject_uuid": str(
            test_experimental_imaging_dataset.attribute["subject_uuid"]
        ),
        "version": 0,
        "attribute": {},
    }
    attributes_to_consider = [
        "path",
        "acquisition_process_uuid",
        "submission_dataset_uuid",
        "subject_uuid",
    ]
    model_dict["uuid"] = dict_to_uuid(model_dict, attributes_to_consider)
    model_dict.pop("path")
    experimentally_captured_image = (
        bia_data_model.ExperimentallyCapturedImage.model_validate(model_dict)
    )
    return experimentally_captured_image


@pytest.fixture()
def attributes_for_image_representation_uuid() -> List[str]:
    return [
        "use_type",
        "original_file_reference_uuid",
        "representation_of_uuid",
    ]


@pytest.fixture()
def representation_dict_template(
    test_experimentally_captured_image, test_file_reference
) -> dict:
    return {
        "image_format": "",
        # "use_type": to be added during test,
        "file_uri": [test_file_reference.uri],
        "original_file_reference_uuid": [test_file_reference.uuid],
        "representation_of_uuid": test_experimentally_captured_image.uuid,
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
                "file_uri": [],
            },
        ),
        (
            None,
            {
                "use_type": "UPLOADED_BY_SUBMITTER",
                "total_size_in_bytes": 10,
            },
        ),
        (
            None,
            {
                "use_type": "INTERACTIVE_DISPLAY",
                "file_uri": [],
            },
        ),
        (
            None,
            {
                "use_type": "THUMBNAIL",
                "file_uri": [],
            },
        ),
    ),
)
def test_create_representation_of_single_image(
    representation_location,
    representation_dict,
    image_creation_result_summary,
    monkeypatch,
    attributes_for_image_representation_uuid,
    representation_dict_template,
    test_experimental_imaging_dataset,
    test_file_reference,
    tmp_path,
):
    accession_id = "S-BIADTEST"
    disk_persister = DiskPersister(
        accession_id=accession_id, output_dir_base=str(tmp_path)
    )
    model_dict = representation_dict_template | representation_dict
    model_dict["uuid"] = bia_ingest.bia_object_creation_utils.dict_to_uuid(
        model_dict, attributes_for_image_representation_uuid
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
        [
            test_experimental_imaging_dataset,
        ]
    )

    created = image_representation.create_image_representation(
        test_file_reference_uuids,
        representation_use_type=representation_dict["use_type"],
        representation_location=representation_location,
        persister=disk_persister,
        result_summary=image_creation_result_summary,
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
