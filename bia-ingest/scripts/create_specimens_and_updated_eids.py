"""Create specimen(s) for expt imaging dataset and save to API. Also update eid attributes

This script creates specimens in the 'correct' way. i.e. all artefacts associationed with the dataset are stored in one specimen. It also updates the experiemental imaging dataset attributes with uuids of the specimen, biosample and image acquisistion method which are needed to create experimentally captured images

It should only be needed for studies that were ingested before the 20/09/2024, as studies ingested afterwards will create the correct Specimens and will update EID during ingest.
"""

import typer
from bia_ingest.config import api_client
from bia_ingest.persistence_strategy import ApiPersister
from bia_ingest.ingest import specimen, experimental_imaging_dataset
from bia_ingest.ingest.biostudies import load_submission
from bia_ingest.cli_logging import IngestionResult

api_persister = ApiPersister(api_client)
app = typer.Typer()


def create_and_persist_specimens(accession_id: str):
    result_summary = {accession_id: IngestionResult()}
    submission = load_submission(accession_id)

    eid = experimental_imaging_dataset.get_experimental_imaging_dataset(
        submission, result_summary
    )
    api_persister.persist(eid)

    for dataset in eid:
        dataset_specimen = specimen.get_specimen_for_dataset(
            submission, dataset, result_summary
        )
        api_persister.persist(
            [
                dataset_specimen,
            ]
        )

    print(result_summary)


@app.command()
def create_and_persist(accession_id: str):
    """
    Creates specimens and updated eids for a given accession ID.
    """
    create_and_persist_specimens(accession_id)


if __name__ == "__main__":
    app()
