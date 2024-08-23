import logging
from typing import List, Any, Dict
from .utils import (
    dicts_to_api_models,
    find_sections_recursive,
    dict_to_uuid,
    persist,
    filter_model_dictionary,
)
from ..biostudies import (
    Submission,
    attributes_to_dict,
)
from bia_shared_datamodels import bia_data_model

logger = logging.getLogger('__main__.'+__name__)


def get_annotation_method(
    submission: Submission, result_summary: dict, persist_artefacts=False
) -> List[bia_data_model.AnnotationMethod]:

    annotation_method_model_dicts = extract_annotation_method_dicts(submission)
    annotation_methods = dicts_to_api_models(
        annotation_method_model_dicts, bia_data_model.AnnotationMethod, result_summary[submission.accno]
    )

    if persist_artefacts and annotation_methods:
        persist(annotation_methods, "annotation_methods", submission.accno)

    return annotation_methods


def extract_annotation_method_dicts(submission: Submission) -> List[Dict[str, Any]]:
    annotation_sections = find_sections_recursive(
        submission.section, ["Annotations"], []
    )

    key_mapping = [
        ("title_id", "Name", ""),
        ("protocol_description", "Annotation overview", ""),
        ("annotation_criteria", "Annotation criteria", ""),
        ("annotation_coverage", "Annotation coverage", ""),
        ("method_type", "Annotation method", "other"),
    ]

    model_dicts = []
    for section in annotation_sections:
        attr_dict = attributes_to_dict(section.attributes)

        model_dict = {k: attr_dict.get(v, default) for k, v, default in key_mapping}

        # TODO: change template to get source dataset information
        model_dict["source_dataset"] = []

        model_dict["accno"] = section.__dict__.get("accno", "")
        model_dict["accession_id"] = submission.accno
        model_dict["uuid"] = generate_annotation_method_uuid(model_dict)
        model_dict["version"] = 1
        model_dict = filter_model_dictionary(
            model_dict, bia_data_model.AnnotationMethod
        )

        model_dicts.append(model_dict)


    logger.info(
        f"Ingesting: {submission.accno}. Created bia_data_model.AnnotationMethod. Count: {len(model_dicts)}"
    )

    return model_dicts


def generate_annotation_method_uuid(protocol_dict: Dict[str, Any]) -> str:
    attributes_to_consider = [
        "accession_id",
        "accno",
        "title_id",
        "protocol_description",
        "annotation_criteria",
        "annotation_coverage",
        "method_type",
        "source_dataset",
    ]
    return dict_to_uuid(protocol_dict, attributes_to_consider)
