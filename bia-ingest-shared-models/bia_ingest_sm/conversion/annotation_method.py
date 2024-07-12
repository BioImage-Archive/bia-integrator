import logging
from typing import List, Any, Dict
from .utils import (
    dicts_to_api_models,
    find_sections_recursive,
    dict_to_uuid,
    persist
)
from ..biostudies import (
    Submission,
    attributes_to_dict,
)
from src.bia_models import bia_data_model

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_annotation_method(
    submission: Submission, persist_artefacts=False
) -> List[bia_data_model.Specimen]:

    annotation_method_model_dicts = extract_annotation_method_dicts(submission)
    annotation_methods = dicts_to_api_models(annotation_method_model_dicts, bia_data_model.AnnotationMethod)

    if persist_artefacts and annotation_methods:
        persist(annotation_methods, "annotation_method", submission.accno)
    
    return annotation_methods


def extract_annotation_method_dicts(submission: Submission) -> List[Dict[str, Any]]:
    annotation_sections = find_sections_recursive(submission.section, ["Annotations"], [])

    key_mapping = [
        ("title_id", "Title", ""),
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
        model_dicts.append(model_dict)

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
        "source_dataset"
    ]
    return dict_to_uuid(protocol_dict, attributes_to_consider)
