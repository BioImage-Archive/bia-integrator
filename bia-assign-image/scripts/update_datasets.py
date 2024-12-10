"""Ad hoc script to update example_image_uris in datasets from v2"""

import typer
import json
from pathlib import Path
import logging

from bia_shared_datamodels import bia_data_model, uuid_creation
from bia_ingest.persistence_strategy import (
    persistence_strategy_factory,
    PersistenceMode,
)
from bia_assign_image.config import settings

logging.basicConfig(
    #    level=logging.INFO, format="%(message)s", handlers=[RichHandler(show_time=False)]
    level=logging.INFO,
    format="%(message)s",
)

logger = logging.getLogger()

app = typer.Typer()


def process_exported_json(exported_json_path: str):
    exported_json = json.loads(Path(exported_json_path).read_text())

    # For test run only process S-BIAD1285
    accession_id_to_process = "S-BIAD1285"

    for old_dataset_uuid, old_dataset in exported_json.items():
        accession_id = old_dataset["submitted_in_study"]["accession_id"]
        example_image_uri = old_dataset["example_image_uri"]
        if not example_image_uri:
            logger.info(
                f"No example URI for dataset {old_dataset_uuid} with accession ID: {accession_id}"
            )
            continue
        if accession_id != accession_id_to_process:
            logger.info(f"Not processing {accession_id}")
            continue

        persister = persistence_strategy_factory(
            PersistenceMode.disk,
            output_dir_base=settings.bia_data_dir,
            accession_id=accession_id,
            # api_client=api_client,
        )
        study_uuid = uuid_creation.create_study_uuid(accession_id=accession_id)
        new_dataset_uuid = uuid_creation.create_dataset_uuid(
            title_id=old_dataset["title_id"], study_uuid=study_uuid
        )
        new_dataset = persister.fetch_by_uuid(
            [
                new_dataset_uuid,
            ],
            bia_data_model.Dataset,
        )[0]
        new_dataset.example_image_uri = example_image_uri
        persister.persist(
            [
                new_dataset,
            ]
        )
        logger.info(f"Saved updated Dataset with UUID {new_dataset.uuid}")


@app.command()
def update_datasets(exported_json_path: str):
    process_exported_json(exported_json_path)


if __name__ == "__main__":
    app()
