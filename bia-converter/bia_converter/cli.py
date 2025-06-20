import sys
import logging
from typing import Optional

import typer
from typing_extensions import Annotated

from bia_converter.bia_api_client import api_client
from bia_converter import convert as convert_module


# TODO - temp to stop import errors - REMOVE!!!
ImageRepresentationUseType = None
app = typer.Typer()


logger = logging.getLogger("bia-converter")


# We need at least two commands because otherwise Typer makes 'convert' the default and arguments get weird
@app.command()
def info():
    pass


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


if __name__ == "__main__":
    app()
