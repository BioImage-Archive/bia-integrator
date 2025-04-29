from typing import List
from uuid import UUID
from pathlib import Path
import pytest
from bia_assign_image import image
from bia_shared_datamodels import bia_data_model

input_data_base_path = Path(__file__).parent / "input_data"
accession_id = "S-BIAD-BIA-ASSIGN-IMAGE-WITH-PATTERN-TEST"

expected_data_base_path = Path(__file__).parent / "data"


@pytest.fixture
def dataset() -> bia_data_model.Dataset:
    # Return Dataset specially created for testing images created from
    # multiple file references. Dataset has file references with pattern
    # "image_{%d}_channel{%d}_slice{%d}_time{%d}"
    dataset_dir = input_data_base_path / "dataset" / accession_id
    dataset_path = next(dataset_dir.glob("*.json"))
    return bia_data_model.Dataset.model_validate_json(dataset_path.read_text())


@pytest.fixture
def image_acquisition_protocol_uuid(
    dataset,
) -> List[UUID]:
    return dataset.attribute[1].value["image_acquisition_protocol_uuid"]


@pytest.fixture
def specimen_imaging_preparation_protocol_uuid(
    dataset,
) -> List[UUID]:
    return dataset.attribute[2].value["specimen_imaging_preparation_protocol_uuid"]


@pytest.fixture
def bio_sample_uuid(dataset) -> List[UUID]:
    return dataset.attribute[3].value["bio_sample_uuid"]


# @pytest.fixture
# def expected_creation_process() -> bia_data_model.CreationProcess:
#    obj_dir = expected_data_base_path / "creation_process" / accession_id
#    obj_path = next(obj_dir.glob("*.json"))
#    return bia_data_model.CreationProcess.model_validate_json(obj_path.read_text())


@pytest.fixture
def expected_image() -> bia_data_model.Image:
    dir = expected_data_base_path / "image" / accession_id
    image_path = next(dir.glob("*.json"))
    return bia_data_model.Image.model_validate_json(image_path.read_text())


@pytest.fixture
def file_references() -> List[bia_data_model.FileReference]:
    file_reference_list = []
    obj_dir = input_data_base_path / "file_reference" / accession_id
    for obj_path in obj_dir.glob("*.json"):
        file_reference = bia_data_model.FileReference.model_validate_json(
            obj_path.read_text()
        )
        if "image_01" in file_reference.file_path:
            file_reference_list.append(file_reference)
        file_reference_list.sort(key=lambda f: str(f.uuid))
    return file_reference_list


def test_bia_image_with_pattern(dataset, file_references, expected_image):
    file_pattern = "image_01_channel{%d}_slice{%d}_time{%d}"
    created_image = image.get_image(
        submission_dataset_uuid=dataset.uuid,
        creation_process_uuid=expected_image.creation_process_uuid,
        file_references=file_references,
        file_pattern=file_pattern,
    )

    assert expected_image == created_image
