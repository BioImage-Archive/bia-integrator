import logging
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    attributes_to_dict,
    find_sections_recursive,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Submission,
    Section,
)

from bia_shared_datamodels import ro_crate_models

logger = logging.getLogger("__main__." + __name__)


def get_annotation_method_by_title(
    submission: Submission,
) -> dict[str, ro_crate_models.AnnotationMethod]:

    sections = find_sections_recursive(
        submission.section, ["Annotations"], []
    )

    roc_object_dict = {}
    for section in sections:
        am = get_annotation_method(section)
        roc_object_dict[am.title] = am
    return roc_object_dict


def get_annotation_method(
    section: Section,
) -> ro_crate_models.AnnotationMethod:
    attr_dict = attributes_to_dict(section.attributes)

    model_dict = {
        "@id": f"biostudies_am:{section.accno}",
        "@type": ["bia:AnnotationMethod"],
        "title": attr_dict["title"],
        "protocolDescription": attr_dict.get("annotation method", ""),
        "methodType": get_annotation_type(attr_dict),
        "annotation_criteria": attr_dict.get("annotation criteria", None),
        "annotation_coverage": attr_dict.get("annotation coverage", None),
    }

    return ro_crate_models.AnnotationMethod(**model_dict)


def get_annotation_type(attr_dict: dict):
    annotation_types = attr_dict.get("annotation type", "")
    if annotation_types:
        if isinstance(annotation_types, str):
            annotation_types = [at.strip() for at in annotation_types.split(",")]
    else:
        annotation_types = ["other"]
    return annotation_types
