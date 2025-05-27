from copy import deepcopy
from bia_shared_datamodels import (
    bia_data_model,
    uuid_creation,
    semantic_models,
    attribute_models,
)
from bia_test_data.mock_objects import mock_dataset, mock_file_reference
from bia_test_data.mock_objects.mock_object_constants import study_uuid

# Use dataset for study component 2 of test data
dataset = mock_dataset.get_dataset()[1]

# Use file references for images in file list of study component 2
file_references = mock_file_reference.get_file_reference()
file_reference_uuids = [f.uuid for f in file_references]

basic_image_dict = {
    "version": 0,
    "object_creator": semantic_models.Provenance.bia_ingest,
    "submission_dataset_uuid": dataset.uuid,
}


def get_image_with_one_file_reference() -> bia_data_model.Image:
    image_dict = deepcopy(basic_image_dict)
    unique_string = " ".join(file_reference_uuids[:1])
    image_dict["uuid"] = uuid_creation.create_image_uuid(study_uuid, unique_string)
    image_dict["original_file_reference_uuid"] = file_reference_uuids[:1]
    creation_process_uuid = uuid_creation.create_creation_process_uuid(
        study_uuid,
        unique_string=f"{image_dict['uuid']}",
    )
    image_dict["creation_process_uuid"] = creation_process_uuid
    attributes = deepcopy(file_references[0].additional_metadata)
    attributes[0].name = f"attributes_from_file_reference_{file_reference_uuids[0]}"
    attributes[0].provenance = semantic_models.Provenance.bia_image_conversion

    file_pattern_attribute_dict = {
        "name": "file_pattern",
        "provenance": semantic_models.Provenance.bia_image_conversion,
        "value": {
            "file_pattern": file_references[0].file_path,
        },
    }
    file_pattern_attribute = semantic_models.Attribute.model_validate(
        file_pattern_attribute_dict
    )
    attributes.append(file_pattern_attribute)
    image_dict["additional_metadata"] = attributes

    uuid_unique_input_dict = {
        "provenance": semantic_models.Provenance.bia_ingest,
        "name": "uuid_unique_input",
        "value": {
            "uuid_unique_input": unique_string,
        },
    }
    image_dict["additional_metadata"].append(
        attribute_models.DocumentUUIDUinqueInputAttribute.model_validate(
            uuid_unique_input_dict
        )
    )

    return bia_data_model.Image.model_validate(image_dict)
