from copy import deepcopy
from bia_shared_datamodels import bia_data_model, uuid_creation, semantic_models
from bia_test_data.mock_objects import mock_dataset, mock_file_reference

# Use dataset for study component 2 of test data
dataset = mock_dataset.get_dataset()[1]

# Use file references for images in file list of study component 2
file_references = mock_file_reference.get_file_reference()
file_reference_uuids = [f.uuid for f in file_references]

basic_image_dict = {
    "version": 0,
    "submission_dataset_uuid": dataset.uuid,
}


def get_image_with_one_file_reference() -> bia_data_model.Image:
    image_dict = deepcopy(basic_image_dict)

    image_dict["uuid"] = uuid_creation.create_image_uuid(
        file_reference_uuid_list=file_reference_uuids[:1]
    )
    image_dict["original_file_reference_uuid"] = file_reference_uuids[:1]
    creation_process_uuid = uuid_creation.create_creation_process_uuid(
        image_uuid=image_dict["uuid"]
    )
    image_dict["creation_process_uuid"] = creation_process_uuid
    attributes = deepcopy(file_references[0].attribute)
    attributes[0].name = f"attributes_from_file_reference_{file_reference_uuids[0]}"
    attributes[0].provenance = semantic_models.AttributeProvenance.bia_conversion

    file_pattern_attribute_dict = {
        "name": "file_pattern",
        "provenance": semantic_models.AttributeProvenance.bia_conversion,
        "value": {
            "file_pattern": file_references[0].file_path,
        },
    }
    file_pattern_attribute = semantic_models.Attribute.model_validate(
        file_pattern_attribute_dict
    )
    attributes.append(file_pattern_attribute)
    image_dict["attribute"] = attributes

    return bia_data_model.Image.model_validate(image_dict)
