import json
import logging
import pathlib
import tempfile
import typer

from enum import Enum
from rich.logging import RichHandler
from typing import Annotated

from annotation_data_converter.api_client import APIMode, get_client
from annotation_data_converter.create_curation_directive import (
    create_ng_link_directive,
    write_directives,
)
from annotation_data_converter.point_annotations import (
    point_annotations,
)
from annotation_data_converter.settings import get_settings
from annotation_data_converter.utils import (
    generate_precomputed_annotation_path_suffix, 
    sync_precomputed_annotation_to_s3, 
)

logging.basicConfig(
    level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
logger = logging.getLogger()

settings = get_settings()
annotation_data_convert = typer.Typer()


class OutputMode(str, Enum):
    BOTH = "both", 
    LOCAL = "local", 
    S3 = "s3",


@annotation_data_convert.command(
    help="Convert star file point annotations into pre-computed neuroglancer objects. Store these in s3 & add links to them from the relevant objects.",
)
def point_annotation_conversion(
    proposal_path: Annotated[
        pathlib.Path,
        typer.Option(
            "--proposal",
            "-p",
            help="Path to the json proposal for the study.",
        ),
    ],
    output_mode: Annotated[
        OutputMode,
        typer.Option(
            "--output-mode",
            "-om",
            case_sensitive=False,
            help="Where to save output; options: local, s3, or both (default).",
        ),
    ] = OutputMode.BOTH,
    output_directory: Annotated[
        pathlib.Path | None,
        typer.Option(
            "--output-directory",
            "-od",
            case_sensitive=False,
            help="Output directory for the data.",
        ),
    ] = settings.default_output_directory,
    api_mode: Annotated[
        APIMode,
        typer.Option(
            "--api-mode",
            "-am",
            case_sensitive=False,
            help="Mode to persist the data. Options: local_api, bia_api. ",
        ),
    ] = APIMode.LOCAL_API,
):
    api_client = get_client(api_mode)

    with open(proposal_path.absolute(), "r") as proposal_file:
        list_of_group_proposals: list[dict] = json.loads(
            proposal_file.read(),
        )

    proposal_list = point_annotations.collect_proposals(list_of_group_proposals)
    directives = []

    for proposal in proposal_list:
        # Note, returns image and annotation data as these objects will need curating to add the s3 links.
        image_rep, image, annotation_data, file_reference = (
            point_annotations.fetch_api_object_dependencies(
                proposal.annotation_data_uuid,
                proposal.image_representation_uuid,
                api_client,
            )
        )

        converter = point_annotations.create_converter(
            image_representation=image_rep,
            annotation_data_file_reference=file_reference,
            proposal=proposal,
        )

        converter.load()
        converter.validate_points()

        precomputed_annotation_path_suffix = generate_precomputed_annotation_path_suffix(
            annotation_data.uuid,
            image,
            api_client, 
        )

        if output_mode in [OutputMode.LOCAL, OutputMode.BOTH]:
            local_output_path = output_directory / precomputed_annotation_path_suffix
            converter.convert_to_neuroglancer_precomputed(local_output_path)

        if output_mode in [OutputMode.S3, OutputMode.BOTH]:
            if output_mode == OutputMode.S3:
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = pathlib.Path(temp_dir) / precomputed_annotation_path_suffix
                    converter.convert_to_neuroglancer_precomputed(temp_path)
                    precomputed_annotation_url = sync_precomputed_annotation_to_s3(
                        str(temp_path), 
                        precomputed_annotation_path_suffix, 
                    )
            else:
                precomputed_annotation_url = sync_precomputed_annotation_to_s3(
                    str(local_output_path), 
                    precomputed_annotation_path_suffix, 
                )

        if output_mode in [OutputMode.S3, OutputMode.BOTH]:
            ng_view_link = converter.generate_neuroglancer_view_link(
                precomputed_annotation_url, 
            )
            directives.append(create_ng_link_directive(ng_view_link, image_rep.uuid))
        elif output_mode == OutputMode.LOCAL and settings.local_annotations_server:
            # Construct local URL for preview
            local_url = f"{settings.local_annotations_server.rstrip('/')}/{precomputed_annotation_path_suffix}"
            converter.generate_neuroglancer_view_link(local_url)
            
    write_directives(directives)


if __name__ == "__main__":
    annotation_data_convert()
