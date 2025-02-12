from typing import Union
from uuid import UUID
from enum import Enum
import typer
from typing_extensions import Annotated

from bia_shared_datamodels.semantic_models import ImageRepresentationUseType
from bia_converter.bia_api_client import api_client, update_object_in_api_idempotent

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
    representation_uuid: Union[UUID, str],
    update_mode: UpdateMode = UpdateMode.REPLACE,
) -> bool:
    try:
        representation = api_client.get_image_representation(representation_uuid)
    except Exception as e:
        logger.error(f"Could not retrieve image representation. Error was {e}.")
        return False
    if representation.use_type == ImageRepresentationUseType.STATIC_DISPLAY:
        image = api_client.get_image(representation.representation_of_uuid)
        dataset = api_client.get_dataset(image.submission_dataset_uuid)
        if update_mode == UpdateMode.REPLACE:
            dataset.example_image_uri = [
                representation.file_uri[0],
            ]
        elif update_mode == UpdateMode.APPEND:
            dataset.example_image_uri.append(representation.file_uri[0])
        elif update_mode == UpdateMode.PREPEND:
            dataset.example_image_uri.insert(0, representation.file_uri[0])
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
    else:
        logger.warning(
            f"Cannot update dataset example image uri when image representation use type is {representation.use_type.value}"
        )
        return False


@app.command()
def main(
    representation_uuid: Annotated[
        str,
        typer.Argument(help="UUID for a STATIC_DISPLAY representation of the dataset"),
    ],
    update_mode: Annotated[
        UpdateMode, typer.Option("--update-mode", "-m")
    ] = UpdateMode.REPLACE,
):
    update_example_image_uri(representation_uuid, update_mode)


if __name__ == "__main__":
    app()
