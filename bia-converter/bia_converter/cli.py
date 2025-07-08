import sys
import logging
from typing import Optional

import typer
from typing_extensions import Annotated

from bia_converter.bia_api_client import api_client
from bia_converter import convert as convert_module


app = typer.Typer()


logger = logging.getLogger("bia-converter")


@app.command()
def convert(
    image_rep_uuid: str,
    conversion_function_name: Annotated[
        str, typer.Argument()
    ] = "convert_uploaded_by_submitter_to_interactive_display",
    conversion_config: Annotated[Optional[str], typer.Argument()] = "{}",
):
    logging.basicConfig(level=logging.INFO)

    image_rep = api_client.get_image_representation(image_rep_uuid)

    try:
        conversion_function = getattr(convert_module, conversion_function_name)

    except AttributeError as e:
        logger.error(
            f"Cannot find conversion function named {conversion_function_name}. Error was {e}"
        )
        sys.exit(2)

    conversion_function(image_rep)

@app.command()
def update_recommended_vizarr_representation(
    image_rep_uuid: str,
):
    logging.basicConfig(level=logging.INFO)

    image_rep = api_client.get_image_representation(image_rep_uuid)
    convert_module.update_recommended_vizarr_representation_for_image(image_rep)
    logger.info(f"Updated recommended vizarr representation of image with uuid {image_rep.representation_of_uuid} to {image_rep.file_uri}")

@app.command()
def create_thumbnail(
    image_rep_uuid: str,
):
    logging.basicConfig(level=logging.INFO)

    image_rep = api_client.get_image_representation(image_rep_uuid)
    thumbnail_uri = convert_module.convert_interactive_display_to_thumbnail(image_rep)
    logger.info(f"Created thumbnail at {thumbnail_uri}")


@app.command()
def create_static_display(
    image_rep_uuid: str,
):
    logging.basicConfig(level=logging.INFO)

    image_rep = api_client.get_image_representation(image_rep_uuid)
    static_display_uri = convert_module.convert_interactive_display_to_static_display(image_rep)
    logger.info(f"Created static display at {static_display_uri}")


if __name__ == "__main__":
    app()
