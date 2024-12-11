from typing import List
from bia_shared_datamodels import bia_data_model, semantic_models
from bia_shared_datamodels.uuid_creation import create_annotation_method_uuid
from .mock_object_constants import study_uuid


def get_annotation_method() -> List[bia_data_model.AnnotationMethod]:

    title_id = "Segmentation masks"
    object_dicts = [
        {
            "uuid": create_annotation_method_uuid(title_id, study_uuid),
            "title_id": title_id,
            "protocol_description": "Test annotation overview 1",
            "annotation_criteria": "Test annotation criteria 1",
            "annotation_coverage": None,
            "method_type": [
                semantic_models.AnnotationMethodType("other"),
            ],
            "version": 0,
        },
    ]

    bia_objects = [
        bia_data_model.AnnotationMethod.model_validate(object_dict)
        for object_dict in object_dicts
    ]
    return bia_objects


def get_annotation_method_as_map():
    return {obj.title_id: obj for obj in get_annotation_method()}
