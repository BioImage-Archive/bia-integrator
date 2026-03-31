import typer
import logging
import json
from rich.logging import RichHandler
from typing_extensions import Annotated
from pathlib import Path
from bia_export.website_export.export_all import (
    get_study_ids,
    study_sort_key,
    get_all_studies,
    write_json,
    write_elastic_bulk_ndjson_gz_chunks,
)

from bia_export.website_export.studies.retrieve import retrieve_study, retrieve_datasets
from bia_integrator_api.models import Study as apiStudy
from .website_export.studies.transform import transform_study
from .website_export.studies.models import StudyCLIContext, CacheUse
from .website_export.images.transform import transform_images
from .website_export.images.models import ImageCLIContext
from .website_export.datasets_for_images.transform import transform_datasets
from .website_export.website_models import CLIContext
from typing import List, Optional, Type
from uuid import UUID
from .bia_client import api_client
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeElapsedColumn,
)

logging.basicConfig(
    level=logging.WARNING,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)
logger = logging.getLogger()

app = typer.Typer()
website = typer.Typer()
app.add_typer(website, name="website")


DEFAULT_WEBSITE_STUDY_FILE_NAME = "bia-study-metadata.json"
DEFAULT_WEBSITE_IMAGE_FILE_NAME = "bia-image-metadata.json"
DEFAULT_WEBSITE_DATASET_FOR_IMAGE_FILE_NAME = "bia-dataset-metadata-for-images.json"


def process_study_for_generate_all(
    study_or_id: str | apiStudy,
    root_directory: Optional[Path],
):
    context_study = create_cli_context(
        StudyCLIContext,
        study_or_id=study_or_id,
        root_directory=root_directory,
    )
    context_image = create_cli_context(
        ImageCLIContext,
        study_or_id=study_or_id,
        root_directory=root_directory,
    )

    transformed_study = transform_study(context_study)
    transformed_images, _ = transform_images(context_image)

    return (
        transformed_study.accession_id,
        transformed_study.model_dump(mode="json"),
        transformed_images,
    )


def generate_output_path(dir_path: Optional[Path], file_name: str) -> Path:
    return dir_path / file_name if dir_path else Path(file_name)


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
        typer.Option("--out_dir", "-o"),
    ] = None,
    update_path: Annotated[
        Optional[Path],
        typer.Option(
            "--update_path",
            "-u",
            help="If update path specified then update the files there (assuming files have the default naming)",
        ),
    ] = None,
    max_workers: Annotated[
        int,
        typer.Option(
            "--workers", "-w", help="Number of parallel workers", min=1, max=5
        ),
    ] = 2,
    write_bulk_gzip: Annotated[
        bool,
        typer.Option("--bulk-gzip", "-c", help="Write gzipped Elastic bulk NDJSON"),
    ] = False,
):
    validate_cli_inputs(id_list=id_list, update_path=update_path)

    studies = resolve_studies(id_list=id_list, root_directory=root_directory)

    studies_map = {}
    image_map = {}

    update_file_study = (
        generate_output_path(update_path, DEFAULT_WEBSITE_STUDY_FILE_NAME)
        if update_path
        else None
    )
    if update_file_study:
        studies_map |= file_data_to_update(update_file_study)

    update_file_image = (
        generate_output_path(update_path, DEFAULT_WEBSITE_IMAGE_FILE_NAME)
        if update_path
        else None
    )
    if update_file_image:
        image_map |= file_data_to_update(update_file_image)

    output_filename_study = generate_output_path(
        output_directory, DEFAULT_WEBSITE_STUDY_FILE_NAME
    )
    output_filename_image = generate_output_path(
        output_directory, DEFAULT_WEBSITE_IMAGE_FILE_NAME
    )

    warnings_list: list[str] = []
    errors_list: list[str] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
    ) as progress:
        task_id = progress.add_task("Processing studies...", total=len(studies))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_study = {
                executor.submit(
                    process_study_for_generate_all,
                    study,
                    root_directory,
                ): study
                for study in studies
            }

            for future in as_completed(future_to_study):
                study_item = future_to_study[future]

                study_label = (
                    study_item.accession_id
                    if isinstance(study_item, apiStudy)
                    else str(study_item)
                )

                progress.update(task_id, description=f"Processing study {study_label}")

                try:
                    accession_id, study_json, transformed_images = future.result()
                    studies_map[accession_id] = study_json
                    image_map |= transformed_images
                except Exception as exc:
                    message = f"Failed to process study {study_label}: {exc}"
                    logger.error(message)
                    errors_list.append(message)
                finally:
                    progress.advance(task_id)

    sorted_map = sort_studies(studies_map, should_sort=bool(id_list))
    if write_bulk_gzip:
        write_elastic_bulk_ndjson_gz_chunks(
            output_prefix=generate_output_path(
                output_directory, "api-study-metadata.bulk"
            ),
            documents=sorted_map,
            index_name="test_index",
            description="Elastic bulk study export",
        )
        write_elastic_bulk_ndjson_gz_chunks(
            output_prefix=generate_output_path(
                output_directory, "api-image-metadata.bulk"
            ),
            documents=image_map,
            index_name="test_index_images",
            description="Elastic bulk image export",
        )
    else:
        write_json(
            path=output_filename_study, data=sorted_map, description="study info"
        )
        write_json(
            path=output_filename_image, data=image_map, description="website images"
        )

    if warnings_list:
        logger.warning(f"{len(warnings_list)} warning(s) occurred")

    if errors_list:
        logger.error(f"{len(errors_list)} error(s) occurred")
        for err in errors_list:
            logger.error(err)


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

    studies = resolve_studies(id_list=id_list, root_directory=root_directory)

    studies_map = {}

    if update_file:
        studies_map |= file_data_to_update(update_file)

    for study in studies:
        context = create_cli_context(
            StudyCLIContext, study_or_id=study, root_directory=root_directory
        )
        study = transform_study(context)
        studies_map[study.accession_id] = study.model_dump(mode="json")
    sorted_map = sort_studies(studies_map, bool(id_list))
    write_json(path=output_filename, data=sorted_map, description="study info")


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

    studies = resolve_studies(id_list=id_list, root_directory=root_directory)

    image_map = {}
    if update_file:
        image_map |= file_data_to_update(update_file)

    for study in studies:
        context = create_cli_context(
            ImageCLIContext, study_or_id=study, root_directory=root_directory
        )
        transformed_images, image_format = transform_images(context)
        image_map |= transformed_images

    write_json(path=output_filename, data=image_map, description="website images")


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

    id_list = resolve_study_ids(id_list=id_list, root_directory=root_directory)

    dataset_map = {}
    if update_file:
        dataset_map |= file_data_to_update(update_file)

    for id in id_list:
        context = create_cli_context(
            CLIContext, id, root_directory, include_dataset=False
        )
        dataset_map |= transform_datasets(context)

    write_json(
        path=output_filename, data=dataset_map, description="datasets for images"
    )


def create_cli_context(
    cli_type: Type[CLIContext],
    study_or_id: str | apiStudy,
    root_directory: Optional[Path],
    cache_use: Optional[CacheUse] = None,
    include_dataset: bool = True,
):
    if root_directory:
        accession_id = (
            study_or_id.accession_id
            if isinstance(study_or_id, apiStudy)
            else study_or_id
        )
        context = cli_type.model_validate(
            {
                "root_directory": root_directory.resolve(),
                "accession_id": accession_id,
                "cache_use": cache_use,
                "study": None,
                "dataset": None,
            }
        )
        context.study = retrieve_study(context=context)
        if include_dataset:
            context.dataset = retrieve_datasets(context=context)
        return context

    if isinstance(study_or_id, apiStudy):
        study = study_or_id
    else:
        study = get_study_from_id(study_or_id)

    context = cli_type.model_validate(
        {
            "study_uuid": str(study.uuid),
            "accession_id": study.accession_id,
            "cache_use": cache_use,
            "study": study,
            "dataset": None,
        }
    )
    if include_dataset:
        context.dataset = retrieve_datasets(context=context)
    return context


def resolve_studies(
    id_list: Optional[List[str]], root_directory: Optional[Path]
) -> List[str] | List[apiStudy]:
    return get_all_studies(root_directory) if not id_list else id_list


def resolve_study_ids(
    id_list: Optional[List[str]], root_directory: Optional[Path]
) -> List[str]:
    return get_study_ids(root_directory) if not id_list else id_list


def is_uuid(id: str) -> bool:
    try:
        UUID(id)
    except:
        return False
    return True


def sort_studies(studies_map: dict, should_sort: bool) -> dict:
    if not should_sort:
        return studies_map
    return dict(
        sorted(
            studies_map.items(),
            key=lambda item: study_sort_key(item[1]),
            reverse=True,
        )
    )


def get_study_from_id(id: str) -> apiStudy:
    if is_uuid(id):
        study = api_client.get_study(id)
    else:
        study = api_client.search_study_by_accession(accession_id=id)
    if study:
        return study
    else:
        logger.error(f"Could not find Study: {id} in API")
        raise RuntimeError(f"Could not find Study with id: {id} in API")


def validate_cli_inputs(
    id_list: Optional[List[str]] = None,
    update_file: Optional[Path] = None,
    update_path: Optional[Path] = None,
    output_file: Optional[Path] = None,
    output_path: Optional[Path] = None,
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

    if output_file and update_file and (output_file.resolve() == update_file.resolve()):
        logger.warning("this is weird")

    if output_path and update_path and (output_path.resolve() == update_path.resolve()):
        logger.warning("this is weird")


def file_data_to_update(file_path: Path) -> Optional[dict]:
    data = None
    with open(file_path, "r") as f:
        data: dict = json.load(f)
    return data


if __name__ == "__main__":
    app()
