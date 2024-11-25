import logging
from typing import List, Any, Dict, Optional

from ...bia_object_creation_utils import (
    dict_to_uuid,
    dict_map_to_api_models,
    filter_model_dictionary,
)

from ...cli_logging import log_model_creation_count
from ..submission_parsing_utils import (
    find_sections_recursive,
    attributes_to_dict,
    case_insensitive_get,
)
from ..api import (
    Submission,
)
from bia_shared_datamodels import bia_data_model, semantic_models
from ...persistence_strategy import PersistenceStrategy

logger = logging.getLogger("__main__." + __name__)


def get_annotation_method_as_map(
    submission: Submission,
    result_summary: dict,
    persister: Optional[PersistenceStrategy] = None,
) -> dict[str, bia_data_model.AnnotationMethod]:
    """
    Returns a dictionary of the form:

    {
      "Annotation Component Title": bia_data_model.AnnotationMethod:(title_id: "Annotation Component Title", uuid:... )
    }

    Where the Key will be the user provided title of the Annotation Component provided by the user.
    There is no annotation method object in biostudies, so no need to link it via associations.
    """

    annotation_method_model_dicts = extract_annotation_method_dicts(submission)
    annotation_methods = dict_map_to_api_models(
        annotation_method_model_dicts,
        bia_data_model.AnnotationMethod,
        result_summary[submission.accno],
    )

    if persister and annotation_methods:
        persister.persist(
            annotation_methods.values(),
        )

    return annotation_methods


def extract_annotation_method_dicts(
    submission: Submission,
) -> dict[str, dict[str, Any]]:
    annotation_sections = find_sections_recursive(submission.section, ["Annotations"])

    key_mapping = [
        ("title_id", "Title", ""),
        ("annotation_criteria", "Annotation Criteria", None),
        ("annotation_coverage", "Annotation Coverage", None),
    ]

    model_dict_map = {}
    for section in annotation_sections:
        attr_dict = attributes_to_dict(section.attributes)

        model_dict = {
            k: case_insensitive_get(attr_dict, v, default)
            for k, v, default in key_mapping
        }

        # TODO: We are not capturing
        # annotation_source_indicator
        # spatial_information
        # transformation_description

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
        model_dict["method_type"] = [
            semantic_models.AnnotationMethodType("other"),
        ]

        model_dict["accno"] = section.__dict__.get("accno", "")
        model_dict["accession_id"] = submission.accno
        model_dict["uuid"] = generate_annotation_method_uuid(model_dict)
        model_dict["version"] = 0
        model_dict = filter_model_dictionary(
            model_dict, bia_data_model.AnnotationMethod
        )

        model_dict_map[attr_dict["Title"]] = model_dict

    return model_dict_map


def generate_annotation_method_uuid(protocol_dict: Dict[str, Any]) -> str:
    attributes_to_consider = [
        "accession_id",
        "accno",
        "title_id",
        "protocol_description",
        "annotation_criteria",
        "annotation_coverage",
        "method_type",
    ]
    return dict_to_uuid(protocol_dict, attributes_to_consider)
