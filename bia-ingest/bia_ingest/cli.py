import typer
from typing import List
from enum import Enum
from typing_extensions import Annotated
from bia_ingest.ingest.biostudies.api import load_submission, load_submission_table_info
from bia_ingest.config import settings, api_client
from bia_ingest.ingest.study import get_study
from bia_ingest.ingest.experimental_imaging_dataset import (
    get_experimental_imaging_dataset,
)
from bia_ingest.ingest.file_reference import get_file_reference_by_dataset
from bia_ingest.ingest.specimen import get_specimen
from bia_ingest.ingest.image_acquisition import get_image_acquisition
from bia_ingest.ingest.image_annotation_dataset import (
    get_image_annotation_dataset,
)
from bia_ingest.ingest.annotation_method import get_annotation_method
from bia_ingest.persistence_strategy import (
    PersistenceMode,
    persistence_strategy_factory,
)

import logging
from rich import print
from rich.logging import RichHandler
from .cli_logging import tabulate_ingestion_errors, IngestionResult

app = typer.Typer()


logging.basicConfig(
    level=logging.INFO, format="%(message)s", handlers=[RichHandler(show_time=False)]
)

logger = logging.getLogger()


class ProcessFilelistMode(str, Enum):
    """Wether to process all file references, ask if there are a lot of files, or always skip."""

    always = "always"
    ask = "ask"
    skip = "skip"


@app.command(help="Ingest from biostudies and echo json of bia_data_model.Study")
def ingest(
    accession_id_list: Annotated[List[str], typer.Argument()],
    persistence_mode: Annotated[
        PersistenceMode, typer.Option(case_sensitive=False)
    ] = PersistenceMode.disk,
    verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False,
    process_filelist: Annotated[
        ProcessFilelistMode, typer.Option(case_sensitive=False)
    ] = ProcessFilelistMode.ask,
    dryrun: Annotated[bool, typer.Option()] = False,
) -> None:
    if verbose:
        logger.setLevel(logging.DEBUG)

    result_summary = {}

    for accession_id in accession_id_list:
        print(f"[blue]-------- Starting ingest of {accession_id} --------[/blue]")
        logger.debug(f"starting ingest of {accession_id}")

        result_summary[accession_id] = IngestionResult()

        persister = None
        if not dryrun:
            persister = persistence_strategy_factory(
                persistence_mode,
                output_dir_base=settings.bia_data_dir,
                accession_id=accession_id,
                api_client=api_client,
            )

        submission = load_submission(accession_id)

        submission_table = load_submission_table_info(accession_id)

        get_study(submission, result_summary, persister=persister)

        experimental_imaging_datasets = get_experimental_imaging_dataset(
            submission, result_summary, persister=persister
        )

        image_annotation_datasets = get_image_annotation_dataset(
            submission, result_summary, persister=persister
        )

        process_files = determine_file_processing(
            process_filelist,
            file_count_limit=200000,
            file_count=submission_table.files,
        )
        if process_files:
            get_file_reference_by_dataset(
                submission,
                experimental_imaging_datasets + image_annotation_datasets,
                result_summary,
                persister=persister,
            )
        else:
            logger.info("Skipping file reference creation.")

        get_image_acquisition(submission, result_summary, persister=persister)

        # Specimen
        # Biosample and Specimen artefacts are processed as part of bia_data_models.Specimen (note - this is very different from Biostudies.Specimen)
        get_specimen(submission, result_summary, persister=persister)

        get_annotation_method(submission, result_summary, persister=persister)

        # typer.echo(study.model_dump_json(indent=2))

        logger.debug(f"COMPLETED: Ingest of: {accession_id}")
        print(f"[green]-------- Completed ingest of {accession_id} --------[/green]")

    print(tabulate_ingestion_errors(result_summary))


def determine_file_processing(
    process_files_mode: ProcessFilelistMode, file_count_limit: int, file_count: int
) -> bool:
    if process_files_mode == ProcessFilelistMode.always:
        process_files = True
    elif process_files_mode == ProcessFilelistMode.skip:
        process_files = False
    elif (
        process_files_mode == ProcessFilelistMode.ask and file_count > file_count_limit
    ):
        process_files = typer.confirm(
            f"The submission has {int(file_count):,} files, which is above the recommended limit of {int(file_count_limit):,}.\n Do you wish to attempt to process them?"
        )
    else:
        process_files = True
    return process_files


@app.callback()
def main() -> None:
    return


if __name__ == "__main__":
    app()
