from bia_shared_datamodels import bia_data_model, semantic_models, uuid_creation
import re


def map_image_representation_to_2025_04_model(
    image_representation_dict: dict, image_2025_04_uuid: str
) -> bia_data_model.ImageRepresentation:
    # Get study accession ID from file uri
    pattern = r"^.*/(S-[A-Za-z0-9_\-]+)/.*$"
    matcher = re.compile(pattern)
    file_uri = ",".join(image_representation_dict["file_uri"])
    accession_id = matcher.findall(file_uri)[0]
    study_uuid = uuid_creation.create_study_uuid(accession_id)

    # TODO: Discuss what unique_str for image_rep uuid should be with Team.
    # For now using str(use_type)+format as unique string
    if isinstance(
        image_representation_dict["use_type"],
        semantic_models.ImageRepresentationUseType,
    ):
        use_type = image_representation_dict["use_type"].value
    else:
        use_type = image_representation_dict["use_type"]
    unique_string = f"{use_type}{image_representation_dict['image_format']}"
    image_representation_uuid = uuid_creation.create_image_representation_uuid(
        study_uuid, unique_string
    )

    image_representation_dict["uuid"] = image_representation_uuid
    image_representation_dict["representation_of_uuid"] = image_2025_04_uuid
    image_representation_dict["object_creator"] = (
        semantic_models.Provenance.bia_image_conversion
    )
    image_representation_dict["voxel_physical_size_x"] = image_representation_dict.pop(
        "physical_size_x"
    )
    image_representation_dict["voxel_physical_size_y"] = image_representation_dict.pop(
        "physical_size_y"
    )
    image_representation_dict["voxel_physical_size_z"] = image_representation_dict.pop(
        "physical_size_z"
    )

    # TODO: Map attributes and add DocumentUUIDUinqueInputAttribute
    image_representation_dict["additional_metadata"] = image_representation_dict.pop(
        "attribute"
    )
    image_representation_dict["additional_metadata"].append(
        {
            "provenance": semantic_models.Provenance.bia_ingest,
            "name": "uuid_unique_input",
            "value": {
                "uuid_unique_input": f"{use_type}{image_representation_dict['image_format']}"
            },
        }
    )

    return bia_data_model.ImageRepresentation.model_validate(image_representation_dict)
