import pdb
import typer
from typing import List
from enum import Enum
from typing import Annotated
from bia_shared_datamodels import bia_data_model, uuid_creation
from bia_ingest.persistence_strategy import (
    PersistenceMode,
    persistence_strategy_factory,
)
from bia_assign_image import (
    image,
    specimen,
    creation_process,
)

import logging

app = typer.Typer()

# TODO: Obtain this from settings
output_dir_base = "/home/kola/.cache/bia-integrator-data-sm"


logging.basicConfig(
#    level=logging.INFO, format="%(message)s", handlers=[RichHandler(show_time=False)]
    level=logging.INFO, format="%(message)s",
)

logger = logging.getLogger()


@app.command(help="Assign listed file references to an image")
def assign(
    accession_id: Annotated[str, typer.Argument()],
    file_reference_uuids: Annotated[List[str], typer.Argument()],
    persistence_mode: Annotated[
        PersistenceMode, typer.Option(case_sensitive=False)
    ] = PersistenceMode.disk,
    dryrun: Annotated[bool, typer.Option()] = False,
) -> None:

    persister = None
    if not dryrun:
        persister = persistence_strategy_factory(
            persistence_mode,
            #output_dir_base=settings.bia_data_dir,
            output_dir_base=output_dir_base,
            accession_id=accession_id,
            #api_client=api_client,
        )
    #pdb.set_trace()
    file_reference_uuid_list = file_reference_uuids[0].split(" ")
    file_references = persister.fetch_by_uuid(file_reference_uuid_list, bia_data_model.FileReference)
    dataset_uuids = [f.submission_dataset_uuid for f in file_references]
    submission_dataset_uuid = dataset_uuids[0]
    assert all([dataset_uuid == submission_dataset_uuid for dataset_uuid in dataset_uuids])
    image_uuid = uuid_creation.create_image_uuid(file_reference_uuid_list)
    creation_process_uuid = uuid_creation.create_creation_process_uuid(image_uuid)
    bia_image = image.get_image(
        submission_dataset_uuid,
        creation_process_uuid,
        original_file_reference_uuid=file_reference_uuid_list,
    )
    logger.info(f"Generated bia.Image object {bia_image}")
    print(f"Generated bia.Image object {bia_image}")


@app.callback()
def main() -> None:
    return


if __name__ == "__main__":
    app()
