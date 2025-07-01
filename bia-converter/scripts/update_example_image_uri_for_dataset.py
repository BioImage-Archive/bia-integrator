from typing import Union
from uuid import UUID
from enum import Enum
import typer
from typing_extensions import Annotated

from bia_integrator_api.exceptions import NotFoundException
from bia_converter.bia_api_client import api_client, update_object_in_api_idempotent
from bia_converter.utils import attributes_by_name

import logging
from rich.logging import RichHandler


class UpdateMode(str, Enum):
    APPEND = "append"
    PREPEND = "prepend"
    REPLACE = "replace"


app = typer.Typer()

logging.basicConfig(
    level=logging.INFO, format="%(message)s", handlers=[RichHandler(show_time=False)]
)

logger = logging.getLogger()


def update_example_image_uri(
    image_uuid: Union[UUID, str],
    update_mode: UpdateMode = UpdateMode.REPLACE,
) -> bool:
    try:
        image = api_client.get_image(f"{image_uuid}")
    except NotFoundException as e:
        logger.error(f"Could not retrieve image. Error was {e}.")
        return False

    dataset = api_client.get_dataset(image.submission_dataset_uuid)
    attributes = attributes_by_name(image)
    image_static_display_uri_key = "image_static_display_uri"
    assert image_static_display_uri_key in attributes
    image_static_display_uri = attributes[image_static_display_uri_key]["slice"]

    if update_mode == UpdateMode.REPLACE:
        dataset.example_image_uri = [
            image_static_display_uri,
        ]
    elif update_mode == UpdateMode.APPEND:
        dataset.example_image_uri.append(image_static_display_uri)
    elif update_mode == UpdateMode.PREPEND:
        dataset.example_image_uri.insert(0, image_static_display_uri)
    else:
        raise (
            Exception(
                f"Invalid update mode {update_mode}. Expected 'APPEND', 'PREPEND' or 'REPLACE'"
            )
        )
    update_object_in_api_idempotent(dataset)

    logger.info(
        f"Updated example image uri of dataset {dataset.uuid} to {dataset.example_image_uri}"
    )
    return True


@app.command()
def main(
    image_uuid: Annotated[
        str,
        typer.Argument(help="UUID for image of the dataset with a static_display view"),
    ],
    update_mode: Annotated[
        UpdateMode, typer.Option("--update-mode", "-m")
    ] = UpdateMode.REPLACE,
):
    update_example_image_uri(image_uuid, update_mode)


if __name__ == "__main__":
    app()
