import typer
import logging
import json
from rich.logging import RichHandler
from typing_extensions import Annotated
from pathlib import Path
from bia_export.website_export.export_all import get_study_ids
from .website_export.studies.transform import transform_study
from .website_export.studies.models import StudyCLIContext, CacheUse
from .website_export.images.transform import transform_images
from .website_export.images.models import ImageCLIContext
from .website_export.datasets_for_images.transform import transform_datasets
from .website_export.website_models import CLIContext
from typing import List, Optional, Type
from uuid import UUID
from .bia_client import api_client
import json
from .settings import Settings
import os

logging.basicConfig(
    level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
logger = logging.getLogger()

app = typer.Typer()
website = typer.Typer()
app.add_typer(website, name="website")


DEFAULT_WEBSITE_STUDY_FILE_NAME = "bia-study-metadata.json"
DEFAULT_WEBSITE_IMAGE_FILE_NAME = "bia-image-metadata.json"
DEFAULT_WEBSITE_DATASET_FOR_IMAGE_FILE_NAME = "bia-dataset-metadata-for-images.json"


@website.command("all")
def generate_all(
    id_list: Annotated[
        Optional[List[str]], typer.Argument(help="IDs of the studies to export")
    ] = None,
    root_directory: Annotated[
        Optional[Path],
        typer.Option(
            "--root",
            "-r",
            help="If root directory specified then use files there, rather than calling API",
        ),
    ] = None,
    output_directory: Annotated[
        Optional[Path],
        typer.Option(
            "--out_dir",
            "-o",
        ),
    ] = None,
    update_path: Annotated[
        Optional[Path],
        typer.Option(
            "--update_path",
            "-u",
            help="If update path specified then update the files there (assuming files have the default naming)",
        ),
    ] = None,
):
    
    validate_cli_inputs(id_list=id_list, update_path=update_path)

    settings = Settings()

    if not id_list:
        id_list = get_study_ids(root_directory)

    logger.info("Exporting study pages")
    website_study(id_list=id_list, root_directory=root_directory, output_filename=(output_directory / DEFAULT_WEBSITE_STUDY_FILE_NAME if output_directory else None))
    logger.info("Exporting image pages")
    website_image(id_list=id_list, root_directory=root_directory, output_filename=(output_directory / DEFAULT_WEBSITE_IMAGE_FILE_NAME if output_directory else None))
    logger.info("Exporting datasets for study pages")
    datasets_for_website_image(id_list=id_list, root_directory=root_directory, output_filename=(output_directory / DEFAULT_WEBSITE_DATASET_FOR_IMAGE_FILE_NAME if output_directory else None))


@website.command("study")
def website_study(
    id_list: Annotated[
        Optional[List[str]], typer.Argument(help="IDs of the studies to export")
    ] = None,
    output_filename: Annotated[
        Optional[Path],
        typer.Option(
            "--out_file",
            "-o",
        ),
    ] = Path(DEFAULT_WEBSITE_STUDY_FILE_NAME),
    root_directory: Annotated[
        Optional[Path],
        typer.Option(
            "--root",
            "-r",
            help="If root directory specified then use files there, rather than calling API",
        ),
    ] = None,
    update_file: Annotated[
        Optional[Path],
        typer.Option(
            "--update_file",
            "-u",
            help="If update file specified then update the file with studies provided.",
        ),
    ] = None,
):

    validate_cli_inputs(id_list=id_list, update_file=update_file)

    settings = Settings()

    if not id_list:
        id_list = get_study_ids(root_directory)

    studies_map = {}
    for id in id_list:
        context = create_cli_context(StudyCLIContext, id, root_directory)
        study = transform_study(context)
        studies_map[study.accession_id] = study.model_dump(mode="json")

    logging.info(f"Writing study info to {output_filename.absolute()}")
    with open(output_filename, "w") as output:
        output.write(json.dumps(studies_map, indent=4))


@website.command("image")
def website_image(
    id_list: Annotated[
        Optional[List[str]], typer.Argument(help="Accession IDs of the study to export")
    ] = None,
    output_filename: Annotated[
        Optional[Path],
        typer.Option(
            "--out_file",
            "-o",
        ),
    ] = Path(DEFAULT_WEBSITE_IMAGE_FILE_NAME),
    root_directory: Annotated[
        Optional[Path],
        typer.Option(
            "--root",
            "-r",
            help="If root directory specified then use files there, rather than calling API",
        ),
    ] = None,
    update_file: Annotated[
        Optional[Path],
        typer.Option(
            "--update_file",
            "-u",
            help="If update file specified then update the file with studies provided.",
        ),
    ] = None,
):
    validate_cli_inputs(id_list=id_list, update_file=update_file)

    settings = Settings()

    if not id_list:
        id_list = get_study_ids(root_directory)

    image_map = {}
    for id in id_list:
        context = create_cli_context(ImageCLIContext, id, root_directory)
        image_map = image_map | transform_images(context)

    logging.info(f"Writing website images to {output_filename.absolute()}")
    with open(output_filename, "w") as output:
        output.write(json.dumps(image_map, indent=4))


@website.command("image-dataset")
def datasets_for_website_image(
    id_list: Annotated[
        Optional[List[str]], typer.Argument(help="Accession IDs of the study to export")
    ] = None,
    output_filename: Annotated[
        Optional[Path],
        typer.Option(
            "--out_file",
            "-o",
        ),
    ] = Path(DEFAULT_WEBSITE_DATASET_FOR_IMAGE_FILE_NAME),
    root_directory: Annotated[
        Optional[Path],
        typer.Option(
            "--root",
            "-r",
            help="If root directory specified then use files there, rather than calling API",
        ),
    ] = None,
    update_file: Annotated[
        Optional[Path],
        typer.Option(
            "--update_file",
            "-u",
            help="If update file specified then update the file with studies provided.",
        ),
    ] = None,
):

    validate_cli_inputs(id_list=id_list, update_file=update_file)

    settings = Settings()

    if not id_list:
        id_list = get_study_ids(root_directory)

    dataset_map = {}
    for id in id_list:
        context = create_cli_context(CLIContext, id, root_directory)
        dataset_map = dataset_map | transform_datasets(context)

    logging.info(f"Writing datasets for images to {output_filename.absolute()}")
    with open(output_filename, "w") as output:
        output.write(json.dumps(dataset_map, indent=4))


def create_cli_context(
    cli_type: Type[CLIContext],
    id: str,
    root_directory: Optional[Path],
    cache_use: Optional[CacheUse] = None,
):
    if root_directory:
        abs_root = root_directory.resolve()
        context = cli_type.model_validate(
            {"root_directory": abs_root, "accession_id": id, "cache_use": cache_use}
        )
    else:
        accession_id = None
        if not is_uuid(id):
            accession_id = id
            id = get_uuid_from_accession_id(accession_id)
        context = cli_type.model_validate(
            {"study_uuid": id, "accession_id": accession_id, "cache_use": cache_use}
        )
    return context


def is_uuid(id: str) -> bool:
    try:
        UUID(id)
    except:
        return False
    return True


def get_uuid_from_accession_id(accession_id: str) -> str:
    study = api_client.search_study_by_accession(accession_id=accession_id)
    if study:
        return study.uuid
    else:
        logger.error(f"Could not find Study: {accession_id} in API")
        raise RuntimeError(
            f"Could not find Study with accession id: {accession_id} in API"
        )


def validate_cli_inputs(
    id_list: Optional[List[str]],
    update_file: Optional[Path],
    update_path: Optional[Path],
):

    if (update_path or update_file) and not id_list:
        raise ValueError(
            "Study IDs must be specified if export website commands are being used in update mode"
        )

    if update_path:
        if not os.path.isdir(update_path):
            raise NotADirectoryError(
                f"Update path: {update_path}, needs to be the directory containing expected files to update."
            )

    if update_file and not os.path.isfile(update_file):
        raise FileNotFoundError(
            f"Update path: {update_path}, needs to be the file to update."
        )


if __name__ == "__main__":
    app()
