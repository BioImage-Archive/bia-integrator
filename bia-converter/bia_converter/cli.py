import sys
import logging
from typing import Optional
import rich
import zarr

import typer
from typing_extensions import Annotated

from bia_integrator_api.models import ImageRepresentationUseType  # type: ignore

from bia_converter.bia_api_client import api_client
from bia_converter.convert import (
    convert_interactive_display_to_thumbnail,
    convert_interactive_display_to_static_display,
    convert_uploaded_by_submitter_to_interactive_display,
    convert_star_annotation_to_json
)
from .io import stage_fileref_and_get_fpath

app = typer.Typer()


logger = logging.getLogger("bia-converter")
logger.setLevel("INFO")


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
    
    image_rep = api_client.get_image_representation(image_rep_uuid)

    try:
        possible_target_dict = SUPPORTED_CONVERSIONS[image_rep.use_type]
        conversion_function = possible_target_dict[target_type]
    except KeyError:
        logger.error(f"Cannot convert from {image_rep.use_type} to {target_type}")
        sys.exit(2)

    conversion_function(image_rep)


@app.command()
def convert_annotation(
    image_rep_uuid: str
):
    """For converting an annotation file, assuming it goes with an already-converted image, 
    accessed via the image reprepresentation, i.e.: 
    image rep. -> image -> listed in creation process -> annotation data.
    Currently annotation data attributes hold "annotated image patterns", 
    listed as {image uuid: image file pattern}"""
    # TODO: add checks for type of conversion as we begin to process different formats
    
    logging.basicConfig(level=logging.INFO)

    image_rep = api_client.get_image_representation(image_rep_uuid)
    image_uuid = image_rep.representation_of_uuid
    creation_process = api_client.get_creation_process_linking_image(image_uuid, page_size=100)
    
    # TODO: check - always only one annotation data linking creation process, or more?
    annotations = []
    for process in creation_process:
        annotation_data = api_client.get_annotation_data_linking_creation_process(process.uuid, page_size=100)
        annotations.extend(annotation_data)
    
    # TODO: for now assume one file ref per annotation data
    for annotation in annotations:
        file_ref = api_client.get_file_reference(annotation.original_file_reference_uuid[0])
        fpath = stage_fileref_and_get_fpath(file_ref)
        convert_star_annotation_to_json(annotation, image_rep, image_uuid, fpath)

    


    



if __name__ == "__main__":
    app()
