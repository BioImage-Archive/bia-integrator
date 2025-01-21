import logging
from typing import Any, Dict, Optional
from uuid import UUID

from bia_ingest.bia_object_creation_utils import dict_map_to_api_models
from bia_ingest.persistence_strategy import PersistenceStrategy

from bia_ingest.biostudies.submission_parsing_utils import (
    find_sections_recursive,
    attributes_to_dict,
    case_insensitive_get,
)
from bia_ingest.biostudies.api import (
    Submission,
)
from bia_shared_datamodels import bia_data_model, semantic_models
from bia_shared_datamodels.uuid_creation import create_annotation_method_uuid

logger = logging.getLogger("__main__." + __name__)


def get_annotation_method_as_map(
    submission: Submission,
    study_uuid: UUID,
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

    annotation_method_model_dicts = extract_annotation_method_dicts(
        submission, study_uuid
    )
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
    study_uuid: UUID,
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

        model_dict["protocol_description"] = attr_dict.get("Annotation Method", "")

        
        annotation_types = attr_dict.get("Annotation Type", "")
        if annotation_types:
            model_dict["method_type"] = [
                semantic_models.AnnotationMethodType(annotation_type.strip())
                for annotation_type in annotation_types.split(",")
            ]
        else:       
            model_dict["method_type"] = [
                semantic_models.AnnotationMethodType("other"),
            ]

        model_dict["uuid"] = create_annotation_method_uuid(
            model_dict["title_id"], study_uuid
        )
        model_dict["version"] = 0

        model_dict_map[attr_dict["Title"]] = model_dict

    return model_dict_map
