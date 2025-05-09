from bia_shared_datamodels import bia_data_model, uuid_creation
import copy
from bia_assign_image.cli import assign
from bia_assign_image.api_client import get_api_client


def map_image_to_2025_04_model(
    old_image_dict: dict,
    accession_id: str,
    file_reference_uuids_2025_04: list,
    dataset_uuid_2025_04: str,
    api_target,
) -> bia_data_model.Image:
    image_dict = copy.deepcopy(old_image_dict)
    image_dict["model"] = {"type_name": "Image", "version": 2}

    # Make file_reference_uuids a list of strings (because of quirky
    # way the typer cli arguments are implemented in bia_assign_image.cli.assign)
    file_reference_uuids = [
        " ".join([str(f) for f in file_reference_uuids_2025_04]),
    ]

    image_uuid = assign(accession_id, file_reference_uuids, api_target)

    api_client = get_api_client(api_target)
    mapped_image = api_client.get_image(image_uuid)
    return bia_data_model.Image.model_validate(mapped_image.to_dict())


def map_image_representation_to_2025_04_model(
    old_image_representation_dict: dict,
    image_2025_04_uuid: str,
    accession_id: str,
) -> bia_data_model.ImageRepresentation:
    image_representation_dict = copy.deepcopy(old_image_representation_dict)

    # Get study accession ID from file uri
    # pattern = r"^.*/(S-[A-Za-z0-9_\-]+)/.*$"
    # matcher = re.compile(pattern)
    # file_uri = ",".join(image_representation_dict["file_uri"])
    # accession_id = matcher.findall(file_uri)[0]
    study_uuid = uuid_creation.create_study_uuid(accession_id)

    image_representation_dict["model"] = {
        "type_name": "ImageRepresentation",
        "version": 4,
    }

    use_type = image_representation_dict.pop("use_type")
    if use_type == "UPLOADED_BY_SUBMITTER":
        unique_string = f"{image_2025_04_uuid}"
        object_creator = "bia_image_assignment"
    elif use_type == "INTERACTIVE_DISPLAY":
        conversion_function = {
            "conversion_function": "map_image_representation_to_2025_04_model"
        }
        unique_string = f"{conversion_function}"
        object_creator = "bia_image_conversion"
    else:
        raise Exception(f"Use type{use_type} is not mapped to 2025/04 models")
    image_representation_uuid = uuid_creation.create_image_representation_uuid(
        study_uuid, unique_string
    )

    image_representation_dict["uuid"] = image_representation_uuid
    image_representation_dict["representation_of_uuid"] = image_2025_04_uuid
    image_representation_dict["object_creator"] = object_creator
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
            "provenance": object_creator,
            "name": "uuid_unique_input",
            "value": {
                "uuid_unique_input": unique_string,
            },
        }
    )

    return bia_data_model.ImageRepresentation.model_validate(image_representation_dict)
