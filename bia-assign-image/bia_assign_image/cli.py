from typing import List, Any
from typing import Annotated
import typer
from bia_shared_datamodels import bia_data_model, uuid_creation, semantic_models
from bia_shared_datamodels.semantic_models import ImageRepresentationUseType
from bia_ingest.persistence_strategy import (
    PersistenceMode,
    persistence_strategy_factory,
)
from bia_assign_image import (
    image,
    specimen,
    creation_process,
)
from bia_assign_image.image_representation import get_image_representation
from bia_assign_image.config import settings, api_client

# For read only client

import logging

app = typer.Typer()
representations_app = typer.Typer()
app.add_typer(
    representations_app,
    name="representations",
    help="Create specified representations",
)

logging.basicConfig(
    #    level=logging.INFO, format="%(message)s", handlers=[RichHandler(show_time=False)]
    level=logging.INFO,
    format="%(message)s",
)

logger = logging.getLogger()


def _get_value_from_attribute_list(
    attribute_list: List[semantic_models.Attribute],
    attribute_name: str,
    default: Any = [],
) -> Any:
    """Get the value of named attribute from a list of attributes"""

    # Assumes attribute.value is a Dict
    return next(
        (
            attribute.value[attribute_name]
            for attribute in attribute_list
            if attribute.name == attribute_name
        ),
        default,
    )


@app.command(help="Assign listed file references to an image")
def assign(
    accession_id: Annotated[str, typer.Argument()],
    file_reference_uuids: Annotated[List[str], typer.Argument()],
    persistence_mode: Annotated[
        PersistenceMode, typer.Option(case_sensitive=False)
    ] = PersistenceMode.disk,
    dryrun: Annotated[bool, typer.Option()] = False,
) -> None:
    persister = persistence_strategy_factory(
        persistence_mode,
        output_dir_base=settings.bia_data_dir,
        accession_id=accession_id,
        api_client=api_client,
    )

    file_reference_uuid_list = file_reference_uuids[0].split(" ")
    file_references = persister.fetch_by_uuid(
        file_reference_uuid_list, bia_data_model.FileReference
    )
    dataset_uuids = [f.submission_dataset_uuid for f in file_references]
    assert len(set(dataset_uuids)) == 1
    submission_dataset_uuid = dataset_uuids[0]
    dataset = persister.fetch_by_uuid(
        [
            submission_dataset_uuid,
        ],
        bia_data_model.Dataset,
    )[0]

    image_uuid = uuid_creation.create_image_uuid(file_reference_uuid_list)

    image_acquisition_protocol_uuid = _get_value_from_attribute_list(
        dataset.attribute, "image_acquisition_protocol_uuid"
    )
    image_preparation_protocol_uuid = _get_value_from_attribute_list(
        dataset.attribute, "specimen_imaging_preparation_protocol_uuid"
    )
    bio_sample_uuid = _get_value_from_attribute_list(
        dataset.attribute, "bio_sample_uuid"
    )
    image_pre_requisites = [
        len(image_acquisition_protocol_uuid),
        len(image_preparation_protocol_uuid),
        len(bio_sample_uuid),
    ]

    assert_error_msg = (
        "Incomplete requisites for creating Specimen AND CreationProcess. "
        + "Need ImageAcquisitionProtocol, SpecimenImagePreparationProtocol and BioSample UUIDs in "
        + "dataset attributes. Got "
        + f"ImageAcquisitionProtocol: {image_acquisition_protocol_uuid},"
        + f"SpecimenImagePreparationProtocol: {image_preparation_protocol_uuid},"
        + f"BioSample: {bio_sample_uuid}"
    )
    assert any(image_pre_requisites) and all(image_pre_requisites), assert_error_msg

    if not any(image_pre_requisites):
        logger.warning(
            "No image_preparation_protocol or bio_sample uuids found in dataset attributes. No Specimen object will be created for this image!"
        )
        bia_specimen = None
    else:
        bia_specimen = specimen.get_specimen(
            image_uuid, image_preparation_protocol_uuid, bio_sample_uuid
        )
        if dryrun:
            logger.info(
                f"Dryrun: Created specimen(s) {bia_specimen}, but not persisting."
            )
        else:
            persister.persist(
                [
                    bia_specimen,
                ]
            )
            logger.info(
                f"Generated bia_data_model.Specimen object {bia_specimen.uuid} and persisted to {persistence_mode}"
            )

    if not bia_specimen:
        logger.warning("Creating CreationProcess with no Specimen")
    if not image_acquisition_protocol_uuid:
        logger.warning("Creating CreationProcess with no ImageAcquisitionProtocol")
    bia_creation_process = creation_process.get_creation_process(
        image_uuid,
        bia_specimen.uuid,
        image_acquisition_protocol_uuid,
    )
    if dryrun:
        logger.info(
            f"Dryrun: Created creation process(es) {bia_creation_process}, but not persisting."
        )
    else:
        persister.persist(
            [
                bia_creation_process,
            ]
        )
        logger.info(
            f"Generated bia_data_model.CreationProcess object {bia_creation_process.uuid} and persisted to {persistence_mode}"
        )

    bia_image = image.get_image(
        submission_dataset_uuid,
        bia_creation_process.uuid,
        file_references=file_references,
    )
    if dryrun:
        logger.info(f"Dryrun: Created Image(s) {bia_image}, but not persisting.")
    else:
        persister.persist(
            [
                bia_image,
            ]
        )
        logger.info(
            f"Generated bia_data_model.Image object {bia_image.uuid} and persisted to {persistence_mode}"
        )


@representations_app.command(help="Create specified representations")
def create(
    accession_id: Annotated[str, typer.Argument()],
    image_uuid_list: Annotated[List[str], typer.Argument()],
    persistence_mode: Annotated[
        PersistenceMode, typer.Option(case_sensitive=False)
    ] = PersistenceMode.disk,
    reps_to_create: Annotated[
        List[ImageRepresentationUseType], typer.Option(case_sensitive=False)
    ] = [
        ImageRepresentationUseType.UPLOADED_BY_SUBMITTER,
        ImageRepresentationUseType.THUMBNAIL,
        ImageRepresentationUseType.INTERACTIVE_DISPLAY,
    ],
    dryrun: Annotated[bool, typer.Option()] = False,
    verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False,
) -> None:
    """Create representations for specified file reference(s)"""

    if verbose:
        logger.setLevel(logging.DEBUG)

    persister = persistence_strategy_factory(
        persistence_mode,
        output_dir_base=settings.bia_data_dir,
        accession_id=accession_id,
        api_client=api_client,
    )

    bia_images = persister.fetch_by_uuid(image_uuid_list, bia_data_model.Image)
    for bia_image in bia_images:
        file_references = persister.fetch_by_uuid(
            bia_image.original_file_reference_uuid, bia_data_model.FileReference
        )
        for representation_use_type in reps_to_create:
            logger.debug(
                f"starting creation of image representation of use type {representation_use_type.value} for Image {bia_image.uuid}"
            )
            image_representation = get_image_representation(
                accession_id,
                file_references,
                bia_image,
                use_type=representation_use_type,
            )
            if image_representation:
                message = f"COMPLETED: Creation of image representation {image_representation.uuid} of use type {representation_use_type.value} for bia_data_model.Image {bia_image.uuid} of {accession_id}"
                logger.info(message)
                if dryrun:
                    logger.info(
                        f"Not persisting image representation:{image_representation}."
                    )
                else:
                    persister.persist(
                        [
                            image_representation,
                        ]
                    )
                    logger.info(
                        f"Persisted image_representation {image_representation.uuid}"
                    )

            else:
                message = f"WARNING: Could NOT create image representation of use type {representation_use_type.value} for bia_data_model.Image {bia_image.uuid} of {accession_id}"
                logger.warning(message)


@app.callback()
def main() -> None:
    return


if __name__ == "__main__":
    app()
