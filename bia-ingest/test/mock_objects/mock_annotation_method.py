from typing import List
from bia_shared_datamodels import bia_data_model, semantic_models
from bia_ingest.bia_object_creation_utils import dict_to_uuid
from .utils import accession_id


def get_annotation_method() -> List[bia_data_model.AnnotationMethod]:
    # For UUID
    attributes_to_consider = [
        "accession_id",
        "accno",
        "title_id",
        "protocol_description",
        "annotation_criteria",
        "annotation_coverage",
        "method_type",
    ]
    annotation_method_info = [
        {
            "accno": "Annotations-29",
            "accession_id": accession_id,
            "title_id": "Segmentation masks",
            "protocol_description": "Test annotation overview 1",
            "annotation_criteria": "Test annotation criteria 1",
            "annotation_coverage": None,
            "method_type": [
                semantic_models.AnnotationMethodType("other"),
            ],
            "version": 0,
        },
    ]

    annotation_method = []
    for annotation_method_dict in annotation_method_info:
        annotation_method_dict["uuid"] = dict_to_uuid(
            annotation_method_dict, attributes_to_consider
        )
        annotation_method_dict.pop("accno")
        annotation_method_dict.pop("accession_id")
        annotation_method.append(
            bia_data_model.AnnotationMethod.model_validate(annotation_method_dict)
        )
    return annotation_method
