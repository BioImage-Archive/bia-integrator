from typing import List
from bia_shared_datamodels import bia_data_model, semantic_models
from bia_shared_datamodels.uuid_creation import create_annotation_method_uuid
from .mock_object_constants import study_uuid


def get_annotation_method() -> List[bia_data_model.AnnotationMethod]:

    title_id = "Segmentation masks"
    unique_string = "Annotations-29"
    object_dicts = [
        {
            "uuid": create_annotation_method_uuid(study_uuid, unique_string),
            "title": title_id,
            "protocol_description": "Test annotation method 1",
            "annotation_criteria": "Test annotation criteria 1",
            "annotation_coverage": None,
            "method_type": [
                semantic_models.AnnotationMethodType(annotation_type.strip())
                for annotation_type in "class_labels, segmentation_mask".split(",")
            ],
            "version": 0,
            "object_creator": "bia_ingest",
            "additional_metadata": [
              {
                "provenance": "bia_ingest",
                "name": "uuid_unique_input",
                "value": {
                  "uuid_unique_input": unique_string,
                }
              }
            ],
        },
    ]

    bia_objects = [
        bia_data_model.AnnotationMethod.model_validate(object_dict)
        for object_dict in object_dicts
    ]
    return bia_objects


def get_annotation_method_as_map():
    return {obj.title: obj for obj in get_annotation_method()}
