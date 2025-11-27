import sys
import logging
import json
from typing import Optional

import typer
from typing_extensions import Annotated

from bia_converter.bia_api_client import api_client
from bia_converter import convert as convert_module
from bia_converter import get_available_conversion_functions
from bia_converter.ng_overlay import generate_overlays, NeuroglancerLayouts

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
    conversion_config_dict = json.loads(conversion_config)

    try:
        conversion_function = getattr(convert_module, conversion_function_name)

    except AttributeError as e:
        logger.error(
            f"Cannot find conversion function named {conversion_function_name}. Error was {e}"
        )
        sys.exit(2)

    conversion_function(image_rep, conversion_config_dict)


@app.command()
def update_recommended_vizarr_representation(
    image_rep_uuid: str,
):
    logging.basicConfig(level=logging.INFO)

    image_rep = api_client.get_image_representation(image_rep_uuid)
    convert_module.update_recommended_vizarr_representation_for_image(image_rep)
    logger.info(
        f"Updated recommended vizarr representation of image with uuid {image_rep.representation_of_uuid} to {image_rep.uuid}"
    )


@app.command()
def create_thumbnail(
    image_rep_uuid: str,
):
    logging.basicConfig(level=logging.INFO)

    image_rep = api_client.get_image_representation(image_rep_uuid)
    thumbnail_uri = convert_module.create_thumbnail_from_interactive_display(image_rep)
    logger.info(f"Created thumbnail at {thumbnail_uri}")


@app.command()
def create_static_display(
    image_rep_uuid: str,
):
    logging.basicConfig(level=logging.INFO)

    image_rep = api_client.get_image_representation(image_rep_uuid)
    static_display_uri = convert_module.create_static_display_from_interactive_display(
        image_rep
    )
    logger.info(f"Created static display at {static_display_uri}")


@app.command()
def generate_neuroglancer_view_link(
    source_image_uuid: Annotated[
        str, typer.Option("--source-image-uuid", help="UUID for the source image")
    ],
    layout: Annotated[
        NeuroglancerLayouts,
        typer.Option("--layout", help="Neuroglancer layout (e.g., xy, 4panel-alt)"),
    ] = NeuroglancerLayouts.XY,
):
    logging.basicConfig(level=logging.INFO)
    generate_overlays(source_image_uuid, layout)
    logger.info(f"Generated neuroglancer view link for {source_image_uuid}")


@app.command()
def list_conversion_functions():
    # TODO: Associate conversion functions with image types they convert
    logging.basicConfig(level=logging.INFO)
    conversion_functions = "\n".join(get_available_conversion_functions())
    logger.info(f"Available conversion functions: {conversion_functions}")


if __name__ == "__main__":
    app()
