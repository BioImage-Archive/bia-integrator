from typing import List
from bia_shared_datamodels import bia_data_model, semantic_models
from bia_ingest.bia_object_creation_utils import dict_to_uuid
from .utils import accession_id
from .mock_image_analysis_method import get_image_analysis_method
from .mock_image_acquisition_protocol import get_image_acquisition_protocol
from .mock_association import get_association_dicts
from .mock_specimen import get_test_specimen_for_image


def get_dataset() -> List[bia_data_model.Dataset]:
    study_uuid = dict_to_uuid(
        {
            "accession_id": accession_id,
        },
        attributes_to_consider=[
            "accession_id",
        ],
    )
    associations = list(get_association_dicts().values())
    specimens = get_test_specimen_for_image()
    image_acquisition_protocol_uuids = [
        str(iap.uuid) for iap in get_image_acquisition_protocol()
    ]

    dataset_dict = {
        "title_id": "Study Component 1",
        "submitted_in_study_uuid": study_uuid,
        "analysis_method": [
            get_image_analysis_method().model_dump(),
        ],
        "correlation_method": [
            # get_template_image_correlation_method().model_dump(),
        ],
        "example_image_uri": [],
        "description": "Description of study component 1",
        "version": 0,
        "attribute": [
            {
                "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                "name": "associations",
                "value": {
                    "associations": associations[0],
                },
            },
            {
                "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                "name": "acquisition_process_uuid",
                "value": {
                    "acquisition_process_uuid": image_acquisition_protocol_uuids,
                },
            },
            {
                "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                "name": "subject_uuid",
                "value": {"subject_uuid": str(specimens[0].uuid)},
            },
            {
                "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                "name": "biosample_uuid",
                "value": {
                    "biosample_uuid": str(specimens[0].sample_of_uuid),
                },
            },
        ],
    }

    dataset_uuid = dict_to_uuid(
        dataset_dict,
        [
            "title_id",
            "submitted_in_study_uuid",
        ],
    )
    dataset_dict["uuid"] = dataset_uuid
    dataset1 = bia_data_model.Dataset.model_validate(dataset_dict)

    dataset_dict = {
        "title_id": "Study Component 2",
        "submitted_in_study_uuid": study_uuid,
        "analysis_method": [
            get_image_analysis_method().model_dump(),
        ],
        "correlation_method": [
            # get_template_image_correlation_method().model_dump(),
        ],
        "example_image_uri": [],
        "description": "Description of study component 2",
        "version": 0,
        "attribute": [
            {
                "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                "name": "associations",
                "value": {
                    "associations": associations[1],
                },
            },
            {
                "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                "name": "acquisition_process_uuid",
                "value": {
                    "acquisition_process_uuid": [
                        image_acquisition_protocol_uuids[0],
                    ]
                },
            },
            {
                "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                "name": "subject_uuid",
                "value": {"subject_uuid": str(specimens[1].uuid)},
            },
            {
                "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                "name": "biosample_uuid",
                "value": {
                    "biosample_uuid": str(specimens[1].sample_of_uuid),
                },
            },
        ],
    }
    dataset_uuid = dict_to_uuid(
        dataset_dict,
        [
            "title_id",
            "submitted_in_study_uuid",
        ],
    )
    dataset_dict["uuid"] = dataset_uuid
    dataset2 = bia_data_model.Dataset.model_validate(dataset_dict)
    return [dataset1, dataset2]
