import typer
from typing import Optional
from typing_extensions import Annotated
from bia_ingest_sm.biostudies import load_submission
from bia_ingest_sm.conversion.study import get_study
from bia_ingest_sm.conversion.experimental_imaging_dataset import (
    get_experimental_imaging_dataset,
)
from bia_ingest_sm.conversion.file_reference import get_file_reference_by_dataset
from bia_ingest_sm.conversion.specimen import get_specimen

app = typer.Typer()


@app.command(help="Ingest from biostudies and echo json of bia_data_model.Study")
def ingest(accession_id: Annotated[str, typer.Argument()],) -> None:
    submission = load_submission(accession_id)

    study = get_study(submission, persist_artefacts=True)

    experimental_imaging_datasets = get_experimental_imaging_dataset(
        submission, persist_artefacts=True
    )

    file_references = get_file_reference_by_dataset(
        submission, experimental_imaging_datasets, persist_artefacts=True
    )

    # Specimen
    # Biosample and Specimen artefacts are processed as part of bia_data_models.Specimen (note - this is very different from Biostudies.Specimen)
    specimens = get_specimen(submission, persist_artefacts=True)

    # typer.echo(study.model_dump_json(indent=2))


@app.callback()
def main() -> None:
    return


if __name__ == "__main__":
    app()
