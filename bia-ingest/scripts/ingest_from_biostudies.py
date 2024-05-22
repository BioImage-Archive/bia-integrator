import rich
import typer

from bia_ingest.models import BIAStudy
from bia_ingest.biostudies import load_submission
from bia_ingest.conversion import extract_model_dict

app = typer.Typer()


@app.command()
def ingest_from_biostudies(accession_id: str) -> None:

    # TODO: Funding
    # TODO: Links
    # TODO: License

    bst_submission = load_submission(accession_id)

    # rich.print(bst_submission)

    model_dict = extract_model_dict(bst_submission)
    model_dict["accession_id"] = accession_id

    bia_study = BIAStudy(**model_dict)

    rich.print(bia_study)

    with open("test_study.json", "w") as fh:
        fh.write(bia_study.json(indent=2))


if __name__ == "__main__":
    app()
