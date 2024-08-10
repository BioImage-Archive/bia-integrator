import typer
from typing import Optional
from typing_extensions import Annotated
from bia_ingest_sm.biostudies import load_submission
from bia_ingest_sm.conversion.study import get_study
from bia_ingest_sm.conversion.experimental_imaging_dataset import get_experimental_imaging_dataset

app = typer.Typer()


@app.command(help="Ingest from biostudies and echo json of bia_data_model.Study")
def ingest(accession_id: Annotated[str, typer.Argument()],) -> None:
    submission = load_submission(accession_id)

    study = get_study(submission, persist_artefacts=True)

    # Biosample, Specimen and ImageAcquisition are processed as part
    # of ExperimentalImaginghttps://app.clickup.com/t/869505ypkDataset
    experimental_imaging_datasets = get_experimental_imaging_dataset(
        submission, persist_artefacts=True
    )

    # FileReference



    # typer.echo(study.model_dump_json(indent=2))


@app.callback()
def main() -> None:
    return


if __name__ == "__main__":
    app()
