import sys
import logging
from typing import Optional

import typer
from typing_extensions import Annotated

from bia_integrator_api.models import ImageRepresentationUseType  # type: ignore

from .bia_api_client import api_client
from .convert import (
    convert_interactive_display_to_thumbnail,
    convert_interactive_display_to_static_display,
    convert_uploaded_by_submitter_to_interactive_display,
)


app = typer.Typer()


logger = logging.getLogger("bia-converter")


SUPPORTED_CONVERSIONS = {
    ImageRepresentationUseType.UPLOADED_BY_SUBMITTER: {
        ImageRepresentationUseType.INTERACTIVE_DISPLAY: convert_uploaded_by_submitter_to_interactive_display
    },
    ImageRepresentationUseType.INTERACTIVE_DISPLAY: {
        ImageRepresentationUseType.THUMBNAIL: convert_interactive_display_to_thumbnail,
        ImageRepresentationUseType.STATIC_DISPLAY: convert_interactive_display_to_static_display,
    },
}


# We need at least two commands because otherwise Typer makes 'convert' the default and arguments get weird
@app.command()
def info():
    pass


@app.command()
def convert(
    image_rep_uuid: str,
    target_type: ImageRepresentationUseType,
    conversion_config: Annotated[Optional[str], typer.Argument()] = "{}",
):
    logging.basicConfig(level=logging.INFO)

    image_rep = api_client.get_image_representation(image_rep_uuid)

    try:
        possible_target_dict = SUPPORTED_CONVERSIONS[image_rep.use_type]
        conversion_function = possible_target_dict[target_type]
    except KeyError:
        logger.error(f"Cannot convert from {image_rep.use_type} to {target_type}")
        sys.exit(2)

    conversion_function(image_rep)


if __name__ == "__main__":
    app()
