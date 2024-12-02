import json
from typing import Dict, List
from pathlib import Path
from bia_shared_datamodels import bia_data_model, semantic_models
from bia_ingest.bia_object_creation_utils import dict_to_uuid
from bia_test_data import bia_test_data_dir
from .utils import accession_id

from .mock_dataset import get_dataset


def get_file_list_data(file_list_name) -> List[Dict]:
    """Return file list contents as dict"""

    file_list_path = bia_test_data_dir / file_list_name
    file_list_data = json.loads(file_list_path.read_text())
    return file_list_data


def get_file_reference_data(filelist: str) -> List[Dict]:
    """Return file reference data for study component 2

    Return file reference data for study component 2. This is the same
    data in ./data/file_list_study_component_2.json
    """

    dataset_index = int(filelist.split("study_component_")[1][0]) - 1
    submission_dataset_uuids = [s.uuid for s in get_dataset()]
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
                "accession_id": accession_id,
                "file_path": fl_data["path"],
                "format": fl_data["type"],
                "size_in_bytes": fl_data["size"],
                "uri": uri_template.format(
                    accession_id=accession_id, file_path=fl_data["path"]
                ),
                "attribute": [
                    attributes_as_attr_dict,
                ],
                "submission_dataset_uuid": submission_dataset_uuids[dataset_index],
            }
        )

    return file_reference_data


# Returns expected FileReference models for study component 2 by default
def get_file_reference(
    filelists: List[str] = [
        "biad_v4/file_list_study_component_2.json",
    ],
) -> List[bia_data_model.FileReference]:
    file_references = []
    for filelist in filelists:
        file_reference_data = get_file_reference_data(filelist)
        file_reference_uuids = get_file_reference_uuid(file_reference_data)
        for file_reference_dict, uuid in zip(file_reference_data, file_reference_uuids):
            file_reference_dict["uuid"] = uuid
            file_reference_dict["version"] = 0
            file_reference_dict.pop("accession_id")
            file_references.append(
                bia_data_model.FileReference.model_validate(file_reference_dict)
            )

    return file_references


def get_file_reference_uuid(file_references: List[Dict[str, str]]) -> List[str]:
    attributes_to_consider = [
        "accession_id",
        "file_path",
        "size_in_bytes",
    ]
    return [
        dict_to_uuid(file_reference, attributes_to_consider)
        for file_reference in file_references
    ]
