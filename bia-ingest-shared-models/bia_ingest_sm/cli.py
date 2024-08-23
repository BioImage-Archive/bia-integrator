import typer
from typing import List
from typing_extensions import Annotated
from bia_ingest_sm.biostudies import load_submission
from bia_ingest_sm.conversion.study import get_study
from bia_ingest_sm.conversion.experimental_imaging_dataset import (
    get_experimental_imaging_dataset,
)
from bia_ingest_sm.conversion.file_reference import get_file_reference_by_dataset
from bia_ingest_sm.conversion.specimen import get_specimen
from bia_ingest_sm.conversion.image_acquisition import get_image_acquisition
from bia_ingest_sm.conversion.image_annotation_dataset import get_image_annotation_dataset
from bia_ingest_sm.conversion.annotation_method import get_annotation_method
import logging
from rich import print
from rich.logging import RichHandler
from .cli_logging import tabulate_errors, ObjectValidationResult

app = typer.Typer()


logging.basicConfig(
    level=logging.INFO, 
    format="%(message)s",
    handlers=[RichHandler(show_time=False)]
)

logger = logging.getLogger()

@app.command(help="Ingest from biostudies and echo json of bia_data_model.Study")
def ingest(accession_id_list: Annotated[List[str], typer.Argument()],
           verbose: Annotated[bool, typer.Option("-v")] = False)  -> None:
    

    if verbose:
        logger.setLevel(logging.DEBUG)

    result_summary = {}

    for accession_id in accession_id_list:
        print(f"[blue]-------- Starting ingest of {accession_id} --------[/blue]")
        logger.debug(f"starting ingest of {accession_id}")

        result_summary[accession_id] = ObjectValidationResult()

        submission = load_submission(accession_id)

        study = get_study(submission, result_summary, persist_artefacts=True)

        experimental_imaging_datasets = get_experimental_imaging_dataset(
            submission, result_summary, persist_artefacts=True
        )

        image_annotation_datasets = get_image_annotation_dataset(
            submission, result_summary, persist_artefacts=True
        )

        file_references = get_file_reference_by_dataset(
            submission, experimental_imaging_datasets + image_annotation_datasets, result_summary, persist_artefacts=True
        )

        image_acquisitions = get_image_acquisition(submission, result_summary, persist_artefacts=True)

        # Specimen
        # Biosample and Specimen artefacts are processed as part of bia_data_models.Specimen (note - this is very different from Biostudies.Specimen)
        specimens = get_specimen(submission, result_summary, persist_artefacts=True)


        annotation_method = get_annotation_method(submission, result_summary, persist_artefacts=True)

        # typer.echo(study.model_dump_json(indent=2))
        
        logger.debug(f"COMPLETED: Ingest of: {accession_id}")
        print(f"[green]-------- Completed ingest of {accession_id} --------[/green]")
    
    print(tabulate_errors(result_summary))



@app.callback()
def main() -> None:
    return


if __name__ == "__main__":
    app()
