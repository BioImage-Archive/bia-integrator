import logging
from typing import List, Any, Dict, Optional

from ..cli_logging import log_model_creation_count
from .utils import (
    dicts_to_api_models,
    find_sections_recursive,
    dict_to_uuid,
    filter_model_dictionary,
)
from .biostudies import (
    Submission,
    attributes_to_dict,
)
from bia_shared_datamodels import bia_data_model
from ..persistence_strategy import PersistenceStrategy

logger = logging.getLogger("__main__." + __name__)


def get_annotation_method(
    submission: Submission,
    result_summary: dict,
    persister: Optional[PersistenceStrategy] = None,
) -> List[bia_data_model.AnnotationMethod]:
    annotation_method_model_dicts = extract_annotation_method_dicts(submission)
    annotation_methods = dicts_to_api_models(
        annotation_method_model_dicts,
        bia_data_model.AnnotationMethod,
        result_summary[submission.accno],
    )

    log_model_creation_count(
        bia_data_model.AnnotationMethod,
        len(annotation_methods),
        result_summary[submission.accno],
    )

    if persister and annotation_methods:
        persister.persist(
            annotation_methods,
        )

    return annotation_methods


def extract_annotation_method_dicts(submission: Submission) -> List[Dict[str, Any]]:
    annotation_sections = find_sections_recursive(
        submission.section, ["Annotations"], []
    )

    key_mapping = [
        ("title_id", "Title", ""),
        ("annotation_criteria", "Annotation Criteria", None),
        ("annotation_coverage", "Annotation Coverage", None),
    ]

    model_dicts = []
    for section in annotation_sections:
        attr_dict = attributes_to_dict(section.attributes)

        model_dict = {k: attr_dict.get(v, default) for k, v, default in key_mapping}

        # TODO: change template to get source dataset information
        model_dict["source_dataset"] = []

        # TODO: Deal with protocol descriptions more consistently.
        if "Annotation Overview" in attr_dict:
            if "Annotation Method" in attr_dict:
                protocol_descrption = (
                    attr_dict.get("Annotation Overview").rstrip(".:,")
                    + ". "
                    + attr_dict.get("Annotation Method")
                )
            else:
                protocol_descrption = attr_dict.get("Annotation Overview")
        else:
            protocol_descrption = attr_dict.get("Annotation Method", "")
        model_dict["protocol_description"] = protocol_descrption

        # TODO: should use "annotation_type" field, but need to update models & deal with more complex mapping logic here.
        model_dict["method_type"] = "other"

        model_dict["accno"] = section.__dict__.get("accno", "")
        model_dict["accession_id"] = submission.accno
        model_dict["uuid"] = generate_annotation_method_uuid(model_dict)
        model_dict["version"] = 0
        model_dict = filter_model_dictionary(
            model_dict, bia_data_model.AnnotationMethod
        )

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
        "source_dataset",
    ]
    return dict_to_uuid(protocol_dict, attributes_to_consider)
