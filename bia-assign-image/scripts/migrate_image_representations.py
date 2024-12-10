"""Ad hoc script to migrate image representations from v2"""

import typer
import json
from pathlib import Path
import subprocess
import logging

from bia_shared_datamodels import bia_data_model, uuid_creation, semantic_models
from bia_shared_datamodels.semantic_models import ImageRepresentationUseType
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
    poetry_base_dir = str(Path(__file__).parent.parent)
    exported_json = json.loads(Path(exported_json_path).read_text())

    # For test run only process S-BIAD1285
    accession_id_to_process = "S-BIAD1285"

    for eci in exported_json.values():
        representations_to_process = []
        accession_id = None
        file_path = None
        for representation in eci["representation"]:
            if (
                len(representation["file_uri"]) > 0
                and representation["file_uri"][0].find(accession_id_to_process) > 0
            ):
                representations_to_process.append(representation)
                if representation["use_type"] == "UPLOADED_BY_SUBMITTER":
                    file_path = representation["file_uri"][0].split(
                        f"{accession_id_to_process}/"
                    )[-1]

        if not representations_to_process or not file_path:
            continue

        # use regex to get accession_id
        accession_id = accession_id_to_process
        persister = persistence_strategy_factory(
            PersistenceMode.disk,
            output_dir_base=settings.bia_data_dir,
            accession_id=accession_id,
            # api_client=api_client,
        )
        old_file_reference_uuid = representation["original_file_reference_uuid"]
        assert len(old_file_reference_uuid) == 1
        study_uuid = uuid_creation.create_study_uuid(accession_id=accession_id)
        new_file_reference_uuid = uuid_creation.create_file_reference_uuid(
            file_path=file_path, study_uuid=study_uuid
        )
        # Create Image
        image_uuid = [
            uuid_creation.create_image_uuid(
                [
                    new_file_reference_uuid,
                ]
            ),
        ]
        image = None
        file_reference_uuid = str(new_file_reference_uuid)

        try:
            image = persister.fetch_by_uuid(image_uuid, bia_data_model.Image)
        except FileNotFoundError:
            logger.info(f"Could not find Image with uuid {image_uuid[0]}. Creating it.")
            result = subprocess.run(
                [
                    "poetry",
                    "--directory",
                    poetry_base_dir,
                    "run",
                    "bia-assign-image",
                    "assign",
                    "--retrieval-mode",
                    "api",
                    accession_id,
                    file_reference_uuid,
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                logger.error(
                    f"Problem creating Image with UUID {image_uuid[0]} for {accession_id}. Error was {result.stderr} - abandoning migration for representations linked to this Image!!!"
                )
                continue
            image = persister.fetch_by_uuid(image_uuid, bia_data_model.Image)
        assert image

        for old_representation in representations_to_process:
            # Create representation
            use_type = old_representation["use_type"]
            logger.info(
                f"Creating new representation for old representation with uuid {old_representation['uuid']}."
            )
            result = subprocess.run(
                [
                    "poetry",
                    "--directory",
                    poetry_base_dir,
                    "run",
                    "bia-assign-image",
                    "representations",
                    "create",
                    "--retrieval-mode",
                    "api",
                    accession_id,
                    str(image_uuid[0]),
                    "--reps-to-create",
                    use_type,
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                logger.error(
                    f"Problem creating ImageRepresentation for old image with UUID {old_representation['uuid']} for {accession_id}. Error was {result.stderr} - abandoning migration for this representation!!!"
                )
                continue
            logger.info(result.stderr)

            # Update representation
            if use_type == ImageRepresentationUseType.UPLOADED_BY_SUBMITTER.value:
                # Nothing to update for this use type
                continue

            new_representation_uuid = uuid_creation.create_image_representation_uuid(
                image_uuid[0], old_representation["image_format"], use_type
            )
            new_representation = persister.fetch_by_uuid(
                [
                    new_representation_uuid,
                ],
                bia_data_model.ImageRepresentation,
            )[0]
            if use_type in (
                ImageRepresentationUseType.STATIC_DISPLAY.value,
                ImageRepresentationUseType.THUMBNAIL.value,
            ):
                # Only need to update file_uri
                new_representation.file_uri = old_representation["file_uri"]
            elif use_type == ImageRepresentationUseType.INTERACTIVE_DISPLAY.value:
                # Update necessary fields and copy over attributes if any
                new_representation.total_size_in_bytes = old_representation[
                    "total_size_in_bytes"
                ]
                new_representation.physical_size_x = old_representation[
                    "physical_size_x"
                ]
                new_representation.physical_size_y = old_representation[
                    "physical_size_y"
                ]
                new_representation.physical_size_z = old_representation[
                    "physical_size_z"
                ]
                new_representation.size_x = old_representation["size_x"]
                new_representation.size_y = old_representation["size_y"]
                new_representation.size_z = old_representation["size_z"]
                new_representation.size_c = old_representation["size_c"]
                new_representation.size_t = old_representation["size_t"]
                new_representation.file_uri = old_representation["file_uri"]

                if old_representation["attribute"]:
                    new_attribute_dict = {
                        "provenance": semantic_models.AttributeProvenance(
                            "bia_conversion"
                        ),
                        "name": "attributes_from_ome.zarr",
                        "value": old_representation["attribute"],
                    }
                    new_representation.attribute = [
                        semantic_models.Attribute.model_validate(new_attribute_dict),
                    ]
            else:
                logger.error(
                    f"Unknown use type: {use_type} Not updating ImageRepresentation with UUID {new_representation.uuid}"
                )
                continue

            # Save updated representation
            persister.persist(
                [
                    new_representation,
                ]
            )
            logger.info(
                f"Saved updated ImageRepresentation with UUID {new_representation.uuid}"
            )


@app.command()
def migrate_image_representations(exported_json_path: str):
    process_exported_json(exported_json_path)


if __name__ == "__main__":
    app()
