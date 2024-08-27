import logging
from typing import List, Dict, Any
from .utils import (
    find_sections_recursive,
    dicts_to_api_models,
    dict_to_uuid,
    persist,
    filter_model_dictionary,
)
import bia_ingest_sm.conversion.study as study_conversion
from ..biostudies import (
    Submission,
    attributes_to_dict,
)
from bia_shared_datamodels import bia_data_model


logger = logging.getLogger('__main__.'+__name__)


def get_image_annotation_dataset(
    submission: Submission, result_summary: dict, persist_artefacts=False
) -> List[bia_data_model.ImageAnnotationDataset]:

    iad_model_dicts = extract_image_annotation_dataset_method_dicts(submission)
    image_annotation_datasets = dicts_to_api_models(
        iad_model_dicts, bia_data_model.ImageAnnotationDataset, result_summary[submission.accno]
    )

    if persist_artefacts and image_annotation_datasets:
        persist(image_annotation_datasets, "image_annotation_datasets", submission.accno)

    return image_annotation_datasets


def extract_image_annotation_dataset_method_dicts(submission: Submission) -> List[Dict[str, Any]]:
    annotation_sections = find_sections_recursive(
        submission.section, ["Annotations"], []
    )

    model_dicts = []
    for section in annotation_sections:
        attr_dict = attributes_to_dict(section.attributes)

        model_dict = {
            "title_id": attr_dict.get("Title", ""),
            "description": attr_dict.get("Description"),
            "submitted_in_study_uuid": study_conversion.get_study_uuid(submission),
            "example_image_uri": [],
            "version": 1,
            "attribute": {},
        }

        model_dict["accno"] = section.__dict__.get("accno", "")
        model_dict["accession_id"] = submission.accno
        model_dict["uuid"] = generate_annotation_method_uuid(model_dict)
        model_dict["version"] = 1
        model_dict = filter_model_dictionary(
            model_dict, bia_data_model.ImageAnnotationDataset
        )

        model_dicts.append(model_dict)


    logger.info(
        f"Ingesting: {submission.accno}. Created bia_data_model.ImageAnnotationDataset. Count: {len(model_dicts)}"
    )

    return model_dicts


def generate_annotation_method_uuid(protocol_dict: Dict[str, Any]) -> str:
    attributes_to_consider = [
        "accession_id",
        "accno",
        "title_id",
    ]
    return dict_to_uuid(protocol_dict, attributes_to_consider)
