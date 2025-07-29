"""Functions and cli tools to fix issues with additional metadata during translational period of 2025/04 model adoption"""

import copy
import logging
import time
from typing import Annotated, List

import typer

from bia_assign_image.api_client import get_api_client, ApiTarget
from bia_integrator_api.models import Attribute, Image
# from bia_shared_datamodels.semantic_models import Attribute

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger()


def fix_thumbnail_uri(uri_dict: dict) -> dict:
    # Convert to bia_data_model AdditionalMetadata attribute
    # This serves as a check that we have the correct structure
    attribute = Attribute.model_validate(uri_dict)
    if "thumbnail_uri" not in attribute.name:
        logger.warning(
            f"Expected attribute with name including 'thumbnail_uri'. Got name: '{attribute.name}' - exiting."
        )
        return uri_dict

    old_value = copy.deepcopy(uri_dict["value"])
    if "256" not in old_value:
        thumbnail_key = next(
            (k for k in old_value.keys() if "thumbnail" in k or "256" in k), ""
        )
        # Case 1 -> value: {"thumbnail_uri": ["http://thumbail_uri"]}
        # import pdb; pdb.set_trace()
        if thumbnail_key == "thumbnail_uri" or thumbnail_key == "image_thumbnail_uri":
            if len(old_value) == 1:
                new_value = {
                    "256": {
                        "uri": old_value[thumbnail_key][0],
                        "size": 256,
                    }
                }
                attribute.name = "image_thumbnail_uri"
                attribute.value = new_value
            else:
                logger.warning(
                    f"Expected value of 'thumbnail_uri' to be list with one entry. Got: {old_value}. Exiting!"
                )
        elif "256" in thumbnail_key:
            if len(old_value) == 2 and "size" in old_value:
                new_value = {
                    "256": {
                        "uri": old_value[thumbnail_key],
                        "size": 256,
                    }
                }
                attribute.name = "image_thumbnail_uri"
                attribute.value = new_value
            else:
                logger.warning(
                    f"Expected value to be a dict with a key such as '256_256' and a key called 'size'. Got: {old_value}. Exiting!"
                )
        else:
            logger.warning(
                f"Could not find expected keys 'thumbnail_uri' or '256_256' in value. Got: {old_value}. Exiting!"
            )
    else:
        logger.warning(
            f"Found key '256' in value - assume nothing to do. Value is {old_value}. Exiting!"
        )

    return attribute.model_dump()


def fix_static_display_uri(uri_dict: dict) -> dict:
    # Convert to bia_data_model AdditionalMetadata attribute
    # This serves as a check that we have the correct structure
    attribute = Attribute.model_validate(uri_dict)
    if "static_display_uri" not in attribute.name:
        logger.warning(
            f"Expected attribute with name including 'static_display_uri'. Got name: '{attribute.name}' - exiting."
        )
        return uri_dict

    old_value = copy.deepcopy(uri_dict["value"])
    # Case 1 -> value: {"static_display_uri": ["http://static_display_uri"]}
    if old_value.get("static_display_uri"):
        assert attribute.name == "static_display_uri"
        assert len(old_value["static_display_uri"]) == 1
        new_value = {
            "slice": {
                "uri": old_value["static_display_uri"][0],
                "size": 512,
            }
        }
        attribute.name = "image_static_display_uri"
        attribute.value = new_value
    elif attribute.name == "image_static_display_uri":
        if "image_static_display_uri" in old_value:
            new_value = {
                "slice": {
                    "uri": old_value["image_static_display_uri"][0],
                    "size": 512,
                }
            }
            attribute.value = new_value
        else:
            assert "slice" in old_value
            if isinstance(old_value["slice"], str):
                static_display_uri = old_value["slice"]
                # Case 2 -> value: {"slice": "http://static_display_uri", "size": (512,512)}
                assert "size" in old_value and (
                    isinstance(old_value["size"], tuple)
                    or isinstance(old_value["size"], list)
                )
                new_value = {
                    "slice": {
                        "uri": static_display_uri,
                        "size": old_value["size"][0],
                    }
                }
                attribute.value = new_value
            elif isinstance(old_value["slice"], dict):
                # Case 3 -> value: {"slice": {"uri": "http://static_display_uri", "size": (512,512)}}
                # Assert this and do nothing
                assert "uri" in old_value["slice"] and isinstance(
                    old_value["slice"]["uri"], str
                )
                assert "size" in old_value["slice"] and (
                    isinstance(old_value["slice"]["size"], tuple)
                    or isinstance(old_value["slice"]["size"], list)
                    or isinstance(old_value["slice"]["size"], int)
                )
                logger.warning(
                    f"Input is already in expected form. Not modifying anything. Got: {old_value}. Exiting!"
                )
    else:
        # We don't know how to handle this -> assert or return unchanged???
        logger.warning(
            f"Did not get expected for of static_display_uri dict. Not modifying anything. Got: {old_value}. Exiting!"
        )

    return attribute.model_dump()


def get_all_images_in_api(api_target: ApiTarget, page_size=1000) -> list:
    api_client = get_api_client(api_target)
    images = []
    start_from_uuid = None

    while True:
        images_from_last_api_call = api_client.search_image(
            page_size=page_size, start_from_uuid=start_from_uuid
        )
        images.extend(images_from_last_api_call)
        if len(images_from_last_api_call) < page_size:
            break
        start_from_uuid = str(images_from_last_api_call[-1].uuid)
        time.sleep(0.1)

    return images


def get_all_images_in_study(
    accession_id: str, api_target: ApiTarget, page_size=100
) -> list:
    api_client = get_api_client(api_target)
    study = api_client.search_study_by_accession(accession_id)
    study_uuid = study.uuid
    datasets = api_client.get_dataset_linking_study(study_uuid, page_size=100)
    assert len(datasets) < 100

    images = []
    for dataset in datasets:
        start_from_uuid = None
        while True:
            images_from_last_api_call = api_client.get_image_linking_dataset(
                uuid=dataset.uuid,
                start_from_uuid=start_from_uuid,
                page_size=page_size,
            )
            images.extend(images_from_last_api_call)
            if len(images_from_last_api_call) < page_size:
                break
            start_from_uuid = str(images_from_last_api_call[-1].uuid)
            time.sleep(0.1)

    return images


def _update_image(image: Image):
    """Update the additional metadata of the thumbnail and static display uri

    Update the additional metadata of the thumbnail and static display uris to be
    those agreed for the 2025/04 models
    """
    updated_image = Image.model_validate(image.model_dump())
    for i, attribute in enumerate(updated_image.additional_metadata):
        if "thumbnail" in attribute.name:
            attr_dict = attribute.model_dump()
            new_attr_dict = fix_thumbnail_uri(attr_dict)
            new_attribute = Attribute.model_validate(new_attr_dict)
            updated_image.additional_metadata[i] = new_attribute
        elif "static_display" in attribute.name:
            attr_dict = attribute.model_dump()
            new_attr_dict = fix_static_display_uri(attr_dict)
            new_attribute = Attribute.model_validate(new_attr_dict)
            updated_image.additional_metadata[i] = new_attribute
    return updated_image


def _update_images(images: list[Image], api_target: ApiTarget, dryrun: bool):
    """Update images and persist or output to screen"""

    if not dryrun:
        api_client = get_api_client(api_target)

    n_images = len(images)
    for i, image in enumerate(images, start=1):
        logger.info(f"Processing image {i} of {n_images}")
        updated_image = _update_image(image)
        if updated_image != image:
            updated_image.version += 1
            if dryrun:
                logger.info("Dryrun: Not persisting updated image:")
                logger.info(updated_image.model_dump_json(indent=2))
            else:
                api_client.post_image(updated_image)
                logger.info(f"Persisted updated image with uuid {image.uuid}")
        else:
            logger.info(
                f"Image with uuid {image.uuid} already in expected form. Nothing to do."
            )


app = typer.Typer()


@app.command(
    help="Update image thumbnail and static display uris to 2025/04 models form"
)
def update_image(
    image_uuid: Annotated[List[str], typer.Argument()],
    api_target: Annotated[
        ApiTarget, typer.Option("--api", "-a", case_sensitive=False)
    ] = ApiTarget.local,
    dryrun: Annotated[bool, typer.Option()] = True,
):
    api_client = get_api_client(api_target)

    images = []
    for uuid in image_uuid:
        images.append(api_client.get_image(uuid))
    _update_images(images, api_target, dryrun)


@app.command(
    help="For given accession id, update image thumbnail and static display uris to 2025/04 models form"
)
def update_images_in_study(
    accession_ids: Annotated[List[str], typer.Argument()],
    api_target: Annotated[
        ApiTarget, typer.Option("--api", "-a", case_sensitive=False)
    ] = ApiTarget.local,
    dryrun: Annotated[bool, typer.Option()] = True,
):
    for accession_id in accession_ids:
        images = get_all_images_in_study(accession_id, api_target)
        _update_images(images, api_target, dryrun)


@app.command(
    help="For all images, update image thumbnail and static display uris to 2025/04 models form"
)
def update_all_images(
    api_target: Annotated[
        ApiTarget, typer.Option("--api", "-a", case_sensitive=False)
    ] = ApiTarget.local,
    dryrun: Annotated[bool, typer.Option()] = True,
):
    images = get_all_images_in_api(api_target)
    _update_images(images, api_target, dryrun)


if __name__ == "__main__":
    app()
