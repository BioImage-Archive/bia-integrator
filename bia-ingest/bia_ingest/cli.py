import typer
from typing import List, Optional
from pathlib import Path
from enum import Enum
from typing import Annotated
from bia_ingest.biostudies.api import (
    load_submission,
    load_submission_table_info,
    Submission,
)
from bia_ingest.biostudies.generic_conversion_utils import attributes_to_dict
from bia_ingest.config import settings, api_client
from bia_ingest.persistence_strategy import (
    PersistenceMode,
    persistence_strategy_factory,
)

from bia_ingest.biostudies.biostudies_processing_version import (
    BioStudiesProcessingVersion,
)

from bia_ingest.biostudies.common.study import get_study
from bia_ingest.biostudies.process_submission_v4 import (
    process_submission_v4,
)
from bia_ingest.biostudies.process_submission_default import (
    process_submission_default,
)
from bia_ingest.biostudies.find_bia_studies import (find_unprocessed_studies)

import logging
from rich import print
from rich.logging import RichHandler
from .cli_logging import tabulate_ingestion_errors, write_table, IngestionResult

app = typer.Typer()
find = typer.Typer()
app.add_typer(find, name="find")


logging.basicConfig(
    level=logging.INFO, format="%(message)s", handlers=[RichHandler(show_time=False)]
)

logger = logging.getLogger()


class ProcessFilelistMode(str, Enum):
    """Wether to process all file references, ask if there are a lot of files, or always skip."""

    always = "always"
    ask = "ask"
    skip = "skip"


@find.command("new-biostudies-studies")
def find_new_studies(
    output_file: Annotated[Optional[Path], typer.Option("--output_file", "-o")] = None
):
    find_unprocessed_studies(output_file)


@app.command(help="Ingest from biostudies and echo json of bia_data_model.Study")
def ingest(
    accession_id_list: Annotated[Optional[List[str]], typer.Argument()] = None,
    input_file: Annotated[Optional[Path], typer.Option("--input_file", "-f")] = None,
    persistence_mode: Annotated[
        PersistenceMode, typer.Option(case_sensitive=False)
    ] = PersistenceMode.disk,
    verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False,
    process_filelist: Annotated[
        ProcessFilelistMode, typer.Option(case_sensitive=False)
    ] = ProcessFilelistMode.ask,
    dryrun: Annotated[bool, typer.Option()] = False,
    write_csv: Annotated[str, typer.Option()] = None,
    counts: Annotated[bool, typer.Option("--counts", "-c")] = False,
) -> None:
    if verbose:
        logger.setLevel(logging.DEBUG)

    result_summary = {}

    if input_file and not accession_id_list:
        accession_id_list = read_file_input(input_file)

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

        try:
            # Get information from biostudies
            submission = load_submission(accession_id)
            submission_table = load_submission_table_info(accession_id)
        except AssertionError as error:
            logger.error("Failed to retrieve information from BioStudies")
            result_summary[accession_id].__setattr__(
                "Uncaught_Exception",
                "Non-200 repsonse from BioStudies",
            )
            logging.exception("message")
            continue
        except Exception as error:
            logger.error("Failed to parse information from BioStudies")
            result_summary[accession_id].__setattr__(
                "Uncaught_Exception",
                str(result_summary[accession_id].Uncaught_Exception) + str(error),
            )
            logging.exception("message")
            continue

        processing_version = determine_biostudies_processing_version(submission)
        result_summary[accession_id].ProcessingVersion = processing_version
        process_files = determine_file_processing(
            process_filelist,
            file_count_limit=200000,
            file_count=submission_table.files,
        )

        try:
            if processing_version == BioStudiesProcessingVersion.V4:
                process_submission_v4(
                    submission, result_summary, process_files, persister
                )
            elif processing_version == BioStudiesProcessingVersion.BIOSTUDIES_DEFAULT:
                process_submission_default(
                    submission, result_summary, process_files, persister
                )
            else:
                get_study(submission, result_summary, persister)

        except Exception as error:
            logging.exception("message")
            result_summary[accession_id].__setattr__(
                "Uncaught_Exception",
                str(result_summary[accession_id].Uncaught_Exception) + str(error),
            )

        logger.debug(f"COMPLETED: Ingest of: {accession_id}")
        print(f"[green]-------- Completed ingest of {accession_id} --------[/green]")

    result_table = tabulate_ingestion_errors(result_summary, counts)
    print(result_table)

    if write_csv:
        write_table(result_table, write_csv)


def read_file_input(input_file: Path):
    with open(input_file, "r") as f:
        lines = f.readlines()
    return [accession_id.strip() for accession_id in lines]


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


def determine_biostudies_processing_version(submission: Submission):
    override_map = {
        "S-BIAD43": BioStudiesProcessingVersion.V4,
        "S-BIAD44": BioStudiesProcessingVersion.V4,
        "S-BIAD590": BioStudiesProcessingVersion.V4, 
        "S-BIAD599": BioStudiesProcessingVersion.V4, 
        "S-BIAD628": BioStudiesProcessingVersion.V4, 
        "S-BIAD677": BioStudiesProcessingVersion.V4, 
        "S-BIAD686": BioStudiesProcessingVersion.V4,
        "S-BIAD822": BioStudiesProcessingVersion.V4,
        "S-BIAD843": BioStudiesProcessingVersion.V4,
        "S-BIAD887": BioStudiesProcessingVersion.V4,
        "S-BIAD916": BioStudiesProcessingVersion.V4,
        "S-BIAD970": BioStudiesProcessingVersion.V4,
        "S-BIAD1021": BioStudiesProcessingVersion.V4,
        "S-BIAD1070": BioStudiesProcessingVersion.V4,
        "S-BIAD1076": BioStudiesProcessingVersion.V4,
        "S-BIAD1244": BioStudiesProcessingVersion.V4,
        "S-BIAD1492": BioStudiesProcessingVersion.V4,
        "S-BIAD1518": BioStudiesProcessingVersion.V4,
        "S-BIAD650": BioStudiesProcessingVersion.FALLBACK,  # Uses v4 template but doesn't actually have rembi components
    }
    accession_id = submission.accno
    if accession_id in override_map:
        return override_map[accession_id]
    else:
        submission_attributes = attributes_to_dict(submission.attributes)
        submission_template = submission_attributes.get("Template", None)
        if submission_template == "BioImages.v4":
            return BioStudiesProcessingVersion.V4
        elif submission_template == "Default":
            return BioStudiesProcessingVersion.BIOSTUDIES_DEFAULT
        else:
            return BioStudiesProcessingVersion.FALLBACK


@app.callback()
def main() -> None:
    return


if __name__ == "__main__":
    app()
