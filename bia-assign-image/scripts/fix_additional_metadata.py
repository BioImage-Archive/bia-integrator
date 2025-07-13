"""Functions and cli tools to fix issues with additional metadata during translational period of 2025/04 model adoption"""

from pathlib import Path
from typing import Annotated
import copy
import json
import logging
import typer
from bia_assign_image.api_client import get_api_client, ApiTarget
from bia_shared_datamodels.semantic_models import Attribute
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)


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
        if thumbnail_key == "thumbnail_uri":
            if len(old_value) == 1:
                new_value = {
                    256: {
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
                    256: {
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


def get_images_in_api(api_target: ApiTarget, page_size=100) -> list:
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


def store_images_to_disk(images: list, output_path: Path):
    images_as_dicts = [i.model_dump() for i in images]
    output_path.write_text(json.dumps(images_as_dicts, indent=2))
    print(f"written images to {output_path}")


# ===============CLI stuff=======================
app = typer.Typer()


@app.command(help="Get all images in API and save to disk")
def get_all_images(
    output_path: Annotated[Path, typer.Argument()],
    api_target: Annotated[
        ApiTarget, typer.Option("--api", "-a", case_sensitive=False)
    ] = ApiTarget.local,
):
    images = get_images_in_api(api_target=api_target)
    store_images_to_disk(images, output_path)


if __name__ == "__main__":
    app()
