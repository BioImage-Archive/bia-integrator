import typer
import logging
import pathlib
import json

from annotation_data_converter.point_annotations import (
    point_annotations,
)
from typing import Annotated
from rich.logging import RichHandler
from annotation_data_converter.api_client import get_client, APIMode
from annotation_data_converter.point_annotations.Proposal import (
    PointAnnotationProposal,
)
from annotation_data_converter.settings import get_settings
from annotation_data_converter.create_curation_directive import (
    create_ng_link_directive,
    write_directives,
)

logging.basicConfig(
    level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
logger = logging.getLogger()
annotation_data_convert = typer.Typer()


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
    output_directory: Annotated[
        pathlib.Path,
        typer.Option(
            "--output_directory",
            "-od",
            case_sensitive=False,
            help="Output directory for the data.",
        ),
    ] = get_settings().default_output_directory,
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
        converter.convert_to_neuroglancer_precomputed(
            output_directory / f"{annotation_data.uuid}_{image.uuid}/"
        )

        # TODO: upload result to s3 & update api objects with s3 url
        s3_url = "example url"

        directives.append(create_ng_link_directive(s3_url, image_rep.uuid))
    
    write_directives(directives)


if __name__ == "__main__":
    annotation_data_convert()
