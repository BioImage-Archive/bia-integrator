from typing import List
from bia_shared_datamodels import bia_data_model
from bia_ingest.bia_object_creation_utils import dict_to_uuid

from .utils import accession_id
from .mock_association import get_association_dicts
from .mock_specimen_imaging_preparation_protocol import (
    get_specimen_imaging_preparation_protocol,
)
from .mock_biosample import get_biosample, get_biosample_by_study_component


# This function is written to provide test data for bia_data_model.Image. It currently
# uses correct form of Specimen where all artefacts in association for
# a dataset are in one Specimen object (see https://app.clickup.com/t/8695fqxpy )
# TODO: Consolidate this function and get_test_specimen() into one
def get_test_specimen_for_image() -> List[bia_data_model.Specimen]:
    attributes_to_consider = [
        "accession_id",
        "imaging_preparation_protocol_uuid",
        "sample_of_uuid",
    ]
    imaging_preparation_protocols = {
        ipp.title_id: ipp.uuid for ipp in get_specimen_imaging_preparation_protocol()
    }
    biosamples_by_study_component = get_biosample_by_study_component()

    # Specimens correspond to associations in Experimental Imaging Dataset
    dataset_associations = get_association_dicts()
    specimens = []
    for study_component, associations in dataset_associations.items():
        biosamples = biosamples_by_study_component.get(study_component, [])
        biosample_uuids = [biosample.uuid for biosample in biosamples]
        biosample_uuids.sort()
        specimen_title = associations[0]["specimen"]
        specimen_dict = {
            "imaging_preparation_protocol_uuid": [
                imaging_preparation_protocols[specimen_title]
            ],
            "sample_of_uuid": biosample_uuids,
            "accession_id": accession_id,
        }
        specimen_dict["uuid"] = dict_to_uuid(specimen_dict, attributes_to_consider)
        # Accession ID only needed to generate UUID
        specimen_dict.pop("accession_id")

        specimen_dict["version"] = 0
        specimens.append(bia_data_model.Specimen.model_validate(specimen_dict))
    return specimens


def get_specimen() -> List[bia_data_model.Specimen]:
    attributes_to_consider = [
        "accession_id",
        "imaging_preparation_protocol_uuid",
        "sample_of_uuid",
    ]
    imaging_preparation_protocols = {
        ipp.title_id: ipp.uuid for ipp in get_specimen_imaging_preparation_protocol()
    }
    biosamples = {biosample.title_id: biosample.uuid for biosample in get_biosample()}

    associations = [
        {
            "Biosample": "Test Biosample 1",
            "Specimen": "Test specimen 1",
        },
        {
            "Biosample": "Test Biosample 2 ",
            "Specimen": "Test specimen 1",
        },
        {
            "Biosample": "Test Biosample 2 ",
            "Specimen": "Test specimen 2",
        },
    ]

    specimens = []
    for association in associations:
        biosample_title = association["Biosample"]
        specimen_title = association["Specimen"]
        specimen_dict = {
            "imaging_preparation_protocol_uuid": [
                imaging_preparation_protocols[specimen_title]
            ],
            "sample_of_uuid": [
                biosamples[biosample_title],
            ],
            "accession_id": accession_id,
        }
        specimen_dict["uuid"] = dict_to_uuid(specimen_dict, attributes_to_consider)
        # Accession ID only needed to generate UUID
        specimen_dict.pop("accession_id")

        specimen_dict["version"] = 0
        specimens.append(bia_data_model.Specimen.model_validate(specimen_dict))
    return specimens
