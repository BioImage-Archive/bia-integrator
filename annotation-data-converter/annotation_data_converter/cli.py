import typer
import logging
import pathlib
import yaml

from annotation_data_converter.point_annotations import (
    point_annotations_to_ng_precompute,
)

from typing import Annotated, Optional
from rich.logging import RichHandler
from annotation_data_converter.api_client import get_client, APIMode
from annotation_data_converter.point_annotations import read_point_annotation
from annotation_data_converter.point_annotations.ProcessingMode import ProcessingMode

annotation_data_convert = typer.Typer()

logging.basicConfig(
    level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
logger = logging.getLogger()


@annotation_data_convert.command(
    help="Convert star file point annotations into pre-computed neuroglancer objects. Store these in s3 & add links to them from the relevant objects.",
)
def point_annotation_conversion(
    annotation_data_uuid: Annotated[
        str,
        typer.Option(
            "--annotation-data",
            "-ad",
            help="UUID of the AnnotationData object",
        ),
    ],
    image_representation_uuid: Annotated[
        str,
        typer.Option(
            "--image-representation",
            "-ir",
            help="UUID of the ImageRepresenation object",
        ),
    ],
    proposal_path: Annotated[
        pathlib.Path,
        typer.Option(
            "--proposal",
            "-p",
            help="Path to the yaml propsal of the study.",
        ),
    ],
    processing_mode: Annotated[
        str,
        typer.Option(
            "--processing-mode",
            "-pm",
            help="Path to the yaml propsal of the study.",
        ),
    ],
    api_mode: Annotated[
        APIMode,
        typer.Option(
            "--api-mode",
            "-am",
            case_sensitive=False,
            help="Mode to persist the data. Options: local_api, bia_api",
        ),
    ] = APIMode.LOCAL_API,
):
    api_client = get_client(api_mode)

    with open(proposal_path) as f:
        yaml_file = yaml.safe_load(f)

    image_rep, image, annotation_data, file_reference = (
        point_annotations_to_ng_precompute.fetch_dependencies(
            annotation_data_uuid, image_representation_uuid, api_client
        )
    )

    annotation_data = read_point_annotation.read_point_data_to_dataframe(
        file_reference.uri, file_reference.format
    )

    key_map = ProcessingMode.get(processing_mode)
    if not key_map:
        raise NotImplementedError("")

    filtered_data = point_annotations_to_ng_precompute.filter_point_annotation_data(
        annotation_data,
        yaml_file,
        annotation_file_reference=file_reference,
        image=image,
        pa_key_map=key_map,
    )

    point_annotations_to_ng_precompute.convert_starfile_df_to_ng_precomp(
        filtered_data, "", image_rep, key_map
    )


if __name__ == "__main__":
    annotation_data_convert()
