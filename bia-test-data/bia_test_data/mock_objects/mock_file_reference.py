import json
from typing import Dict, List
from bia_shared_datamodels import bia_data_model, semantic_models
from bia_test_data import bia_test_data_dir
from .mock_object_constants import accession_id, study_uuid, accession_id_default, study_uuid_default
from bia_shared_datamodels.uuid_creation import create_file_reference_uuid
from .mock_dataset import get_dataset, get_default_dataset


def get_file_list_data(file_list_name) -> List[Dict]:
    """Return file list contents as dict"""

    file_list_path = bia_test_data_dir / file_list_name
    file_list_data = json.loads(file_list_path.read_text())
    return file_list_data


def get_file_reference_data(dataset_uuid = get_dataset()[1].uuid, filelist: str = "biad_v4/file_list_study_component_2.json") -> List[Dict]:
    """
    Return file reference data for study component 2

    Return file reference data for study component 2. This is the same
    data in ./data/file_list_study_component_2.json
    """

    uri_template = "https://www.ebi.ac.uk/biostudies/files/{accession_id}/{file_path}"
    file_list_data = get_file_list_data(filelist)

    file_reference_data = []

    for fl_data in file_list_data:
        attributes = {a["name"]: a.get("value", None) for a in fl_data["attributes"]}
        attributes_as_attr_dict = {
            "provenance": semantic_models.AttributeProvenance("bia_ingest"),
            "name": "attributes_from_biostudies.File",
            "value": {
                "attributes": attributes,
            },
        }
        file_reference_data.append(
            {
                "uuid": create_file_reference_uuid(fl_data["path"], study_uuid),
                "file_path": fl_data["path"],
                "format": fl_data["type"],
                "size_in_bytes": int(fl_data["size"]),
                "uri": uri_template.format(
                    accession_id=accession_id, file_path=fl_data["path"]
                ),
                "submission_dataset_uuid": dataset_uuid,
                "version": 0,
                "attribute": [
                    attributes_as_attr_dict,
                ],
            }
        )

    return file_reference_data


# Returns expected FileReference models for study component 2 by default
def get_file_reference(
    dataset_filelist_map: dict = {get_dataset()[1].uuid: "biad_v4/file_list_study_component_2.json"}
) -> List[bia_data_model.FileReference]:
    file_references = []
    for dataset_uuid, filelist in dataset_filelist_map.items():
        file_reference_data = get_file_reference_data(dataset_uuid, filelist)
        for file_reference_dict in file_reference_data:
            file_references.append(
                bia_data_model.FileReference.model_validate(file_reference_dict)
            )

    return file_references


def get_default_file_reference_data(
    file_list: str, 
    dataset_uuid = get_default_dataset().uuid, 
) -> List[Dict]:
    
    uri_template = "https://www.ebi.ac.uk/biostudies/files/{accession_id}/{file_path}"
    file_list_data = get_file_list_data(file_list)

    file_reference_data = []

    for fl_data in file_list_data:
        attributes = {a["name"]: a.get("value", None) for a in fl_data["attributes"]}
        attributes_as_attr_dict = {
            "provenance": semantic_models.AttributeProvenance("bia_ingest"),
            "name": "attributes_from_biostudies.File",
            "value": {
                "attributes": attributes,
            },
        }
        file_reference_data.append(
            {
                "uuid": create_file_reference_uuid(fl_data["path"], study_uuid_default),
                "file_path": fl_data["path"],
                "format": fl_data["type"],
                "size_in_bytes": int(fl_data["size"]),
                "uri": uri_template.format(
                    accession_id=accession_id_default, file_path=fl_data["path"]
                ),
                "submission_dataset_uuid": dataset_uuid,
                "version": 0,
                "attribute": [
                    attributes_as_attr_dict,
                ],
            }
        )

    return file_reference_data