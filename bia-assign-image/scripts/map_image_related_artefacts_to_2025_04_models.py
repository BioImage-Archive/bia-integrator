from bia_shared_datamodels import bia_data_model, uuid_creation, attribute_models
import copy
from bia_assign_image.cli import assign
from bia_assign_image.api_client import get_api_client, store_object_in_api_idempotent


def map_image_to_2025_04_model(
    old_image_dict: dict,
    accession_id: str,
    file_reference_uuids_2025_04: list,
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
        uploaded_by_submitter_rep_uuid = uuid_creation.create_image_representation_uuid(
            study_uuid, unique_string=f"{image_2025_04_uuid}"
        )
        conversion_function = "{'conversion_function': 'map_image_representation_to_2025_04_model'}"
        unique_string = f"{uploaded_by_submitter_rep_uuid} {conversion_function}"
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

    # Always make the version of the newly created image representation 0
    image_representation_dict["version"] = 0

    # Map attributes modifying provenance from 'bia_conversion' if necessary
    attributes = image_representation_dict.pop("attribute")
    image_representation_dict["additional_metadata"] = []
    for attribute in attributes:
        if attribute["provenance"] == "bia_conversion":
            attribute["provenance"] = "bia_image_conversion"
        image_representation_dict["additional_metadata"].append(attribute)

    # Add DocumentUUIDUinqueInputAttribute which is new in 2025_04 models
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


def map_image_related_artefacts_to_2025_04_models(
    file_reference_mapping: dict,
    accession_id: str,
    api_target,
) -> dict:
    file_references_old = file_reference_mapping["file_reference"]
    study_uuid_2025_04 = uuid_creation.create_study_uuid(accession_id)
    file_reference_uuids_2025_04 = []
    for file_reference in file_references_old:
        file_reference_unique_string = (
            f"{file_reference['file_path']}{file_reference['size_in_bytes']}"
        )
        file_reference_uuid = uuid_creation.create_file_reference_uuid(
            study_uuid_2025_04, file_reference_unique_string
        )
        file_reference_uuids_2025_04.append(file_reference_uuid)

    image_dict_old = copy.deepcopy(file_reference_mapping)
    image_dict_old.pop("file_reference")
    image_dict_old.pop("image_representation")
    image_2025_04 = map_image_to_2025_04_model(
        image_dict_old,
        accession_id,
        file_reference_uuids_2025_04,
        api_target=api_target,
    )
    image_2025_04_uuid = f"{image_2025_04.uuid}"

    representations_old = file_reference_mapping["image_representation"]

    uploaded_by_submitter_rep = _get_im_rep_from_im_rep_list(
        representations_old,
        "UPLOADED_BY_SUBMITTER",
    )
    if uploaded_by_submitter_rep:
        rep_of_image_uploaded_by_submitter_2025_04 = (
            map_image_representation_to_2025_04_model(
                uploaded_by_submitter_rep,
                image_2025_04_uuid,
                accession_id,
            )
        )
    else:
        rep_of_image_uploaded_by_submitter_2025_04 = {}

    interactive_display_rep = _get_im_rep_from_im_rep_list(
        representations_old,
        "INTERACTIVE_DISPLAY",
    )
    if interactive_display_rep:
        rep_of_image_converted_to_ome_zarr_2025_04 = (
            map_image_representation_to_2025_04_model(
                interactive_display_rep,
                image_2025_04_uuid,
                accession_id,
            )
        )
    else:
        rep_of_image_converted_to_ome_zarr_2025_04 = {}

    thumbnail_rep = _get_im_rep_from_im_rep_list(
        representations_old,
        "THUMBNAIL",
    )
    if thumbnail_rep:
        thumbnail_uri = attribute_models.Attribute.model_validate(
            {
                "provenance": "bia_image_assignment",
                "name": "thumbnail_uri",
                "value": {"thumbnail_uri": thumbnail_rep["file_uri"]},
            }
        )
        image_2025_04.additional_metadata.append(thumbnail_uri)

    static_display_rep = _get_im_rep_from_im_rep_list(
        representations_old,
        "STATIC_DISPLAY",
    )
    if static_display_rep:
        static_display_uri = attribute_models.Attribute.model_validate(
            {
                "provenance": "bia_image_assignment",
                "name": "static_display_uri",
                "value": {"static_display_uri": static_display_rep["file_uri"]},
            }
        )
        image_2025_04.additional_metadata.append(static_display_uri)
        
    if rep_of_image_converted_to_ome_zarr_2025_04:
        recommended_vizarr_representation = attribute_models.Attribute.model_validate(
            {
                "provenance": "bia_image_assignment",
                "name": "recommended_vizarr_representation",
                "value": {
                    "recommended_vizarr_representation": rep_of_image_converted_to_ome_zarr_2025_04.uuid,
                },
            }
        )
        image_2025_04.additional_metadata.append(recommended_vizarr_representation)


    if thumbnail_rep or static_display_rep or rep_of_image_converted_to_ome_zarr_2025_04:
        # image_2025_04.version += 1
        api_client = get_api_client(api_target)
        store_object_in_api_idempotent(
            api_client,
            image_2025_04,
        )
        image_2025_04 = bia_data_model.Image.model_validate(
            api_client.get_image(image_2025_04_uuid).model_dump()
        )

    return {
        "image": image_2025_04,
        "representation_of_image_uploaded_by_submitter": rep_of_image_uploaded_by_submitter_2025_04,
        "representation_of_image_converted_to_ome_zarr": rep_of_image_converted_to_ome_zarr_2025_04,
    }


def _get_im_rep_from_im_rep_list(
    im_rep_list: list,
    use_type: str,
) -> dict:
    """Get image representation with specified use type from list of reps"""

    return next(
        (rep for rep in im_rep_list if rep["use_type"] == use_type),
        {},
    )
