import typer
import logging
import json
from rich.logging import RichHandler
from typing_extensions import Annotated
from pathlib import Path
from .website_export.studies.transform import transform_study
from .website_export.studies.models import CLIContext as StudyCLIContext
from .website_export.images.transform import transform_ec_images
from .website_export.images.models import CLIContext as ImageCLIContext
from .website_export.datasets_for_images.transform import transform_datasets
from .website_export.website_models import CLIContext
from typing import List
import json

logging.basicConfig(
    level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
logger = logging.getLogger()

app = typer.Typer()


@app.command()
def website_study(
    id_list: Annotated[List[str], typer.Argument(help="IDs of the studies to export")],
    root_directory: Annotated[
        Path,
        typer.Option(
            "--root",
            "-r",
            help="If root directory specified then use files there, rather than calling API",
        ),
    ] = None,
    output_filename: Annotated[
        Path,
        typer.Option(
            "--out_file",
            "-o",
        ),
    ] = Path("bia-images-export.json"),
):

    if root_directory:
        abs_root = root_directory.resolve()

    studies_map = {}
    for id in id_list:
        if abs_root:
            context = StudyCLIContext(root_directory=abs_root, accession_id=id)
        else:
            context = StudyCLIContext(study_uuid=id)
        study = transform_study(context)
        studies_map[study.accession_id] = study.model_dump(mode="json")

    logging.info(f"Writing study info to {output_filename.absolute()}")
    with open(output_filename, "w") as output:
        output.write(json.dumps(studies_map, indent=4))


@app.command()
def website_image(
    id_list: Annotated[
        List[str], typer.Argument(help="Accession ID of the study to export")
    ],
    root_directory: Annotated[
        Path,
        typer.Option(
            "--root",
            "-r",
            help="If root directory specified then use files there, rather than calling API",
        ),
    ] = None,
    output_filename: Annotated[
        Path,
        typer.Option(
            "--out_file",
            "-o",
        ),
    ] = Path("bia-image-export.json"),
):

    if root_directory:
        abs_root = root_directory.resolve()

    image_map = {}
    for id in id_list:
        if abs_root:
            context = ImageCLIContext(root_directory=abs_root, accession_id=id)
        else:
            context = ImageCLIContext(study_uuid=id)

        image_map = image_map | transform_ec_images(context)

    logging.info(f"Writing website images to {output_filename.absolute()}")
    with open(output_filename, "w") as output:
        output.write(json.dumps(image_map, indent=4))


@app.command()
def datasets_for_website_image(
    id_list: Annotated[
        List[str], typer.Argument(help="Accession ID of the study to export")
    ],
    root_directory: Annotated[
        Path,
        typer.Option(
            "--root",
            "-r",
            help="If root directory specified then use files there, rather than calling API",
        ),
    ] = None,
    output_filename: Annotated[
        Path,
        typer.Option(
            "--out_file",
            "-o",
        ),
    ] = Path("bia-image-export.json"),
):

    if root_directory:
        abs_root = root_directory.resolve()

    dataset_map = {}
    for id in id_list:
        if abs_root:
            context = CLIContext(root_directory=abs_root, accession_id=id)
        else:
            context = CLIContext(study_uuid=id)

        dataset_map = dataset_map | transform_datasets(context)

    logging.info(f"Writing datasets for images to {output_filename.absolute()}")
    with open(output_filename, "w") as output:
        output.write(json.dumps(dataset_map, indent=4))


if __name__ == "__main__":
    app()
