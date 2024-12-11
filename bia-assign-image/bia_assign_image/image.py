from uuid import UUID
from typing import List
from bia_shared_datamodels import bia_data_model, semantic_models, uuid_creation

# TODO: Explore just passing original_file_reference_uuid then deriving
#       other UUIDs from this.
def get_image(
        submission_dataset_uuid: UUID,
        creation_process_uuid: UUID,
        file_references: List[bia_data_model.FileReference,],
    ) -> bia_data_model.Image:
    original_file_reference_uuid = [f.uuid for f in file_references]
    model_dict = {
        "version": 0,
        "submission_dataset_uuid": submission_dataset_uuid,
        "creation_process_uuid": creation_process_uuid,
        "original_file_reference_uuid": original_file_reference_uuid,
    }
    
    model_dict["uuid"] = uuid_creation.create_image_uuid(
        original_file_reference_uuid
    )
    model = bia_data_model.Image.model_validate(model_dict)

    # TODO: Add attributes from each file reference
    for file_reference in file_references:
        for attribute in file_reference.attribute:
            if attribute.name == "attributes_from_biostudies.File" and "attributes" in attribute.value:
                new_attribute_dict = {
                    "provenance": semantic_models.AttributeProvenance.bia_conversion,
                    "name": f"attributes_from_file_reference_{file_reference.uuid}",
                    "value": attribute.value,
                }
                model.attribute.append(semantic_models.Attribute.model_validate(new_attribute_dict))


    return model
