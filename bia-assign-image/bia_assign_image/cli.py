from typing import List, Any
from pathlib import Path
from typing import Annotated
import typer
from bia_shared_datamodels import uuid_creation, semantic_models
from bia_assign_image import (
    image,
    specimen,
    creation_process,
    propose,
)
from bia_assign_image.image_representation import get_image_representation
from bia_assign_image.api_client import (
    ApiTarget,
    get_api_client,
    store_object_in_api_idempotent,
)

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
    api_target: Annotated[
        ApiTarget, typer.Option("--api", "-a", case_sensitive=False)
    ] = ApiTarget.prod,
    dryrun: Annotated[bool, typer.Option()] = False,
) -> str:
    api_client = get_api_client(api_target)

    file_reference_uuid_list = file_reference_uuids[0].split(" ")
    file_references = [
        api_client.get_file_reference(f) for f in file_reference_uuid_list
    ]
    dataset_uuids = [f.submission_dataset_uuid for f in file_references]
    assert len(set(dataset_uuids)) == 1
    submission_dataset_uuid = dataset_uuids[0]
    dataset = api_client.get_dataset(submission_dataset_uuid)
    study_uuid = dataset.submitted_in_study_uuid

    image_uuid_unique_string = image.create_image_uuid_unique_string(
        file_reference_uuids
    )
    image_uuid = uuid_creation.create_image_uuid(study_uuid, image_uuid_unique_string)

    image_acquisition_protocol_uuid = _get_value_from_attribute_list(
        dataset.additional_metadata, "image_acquisition_protocol_uuid"
    )
    image_preparation_protocol_uuid = _get_value_from_attribute_list(
        dataset.additional_metadata, "specimen_imaging_preparation_protocol_uuid"
    )
    bio_sample_uuid = _get_value_from_attribute_list(
        dataset.additional_metadata, "bio_sample_uuid"
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
            study_uuid,
            image_uuid,
            image_preparation_protocol_uuid,
            bio_sample_uuid,
        )
        if dryrun:
            logger.info(
                f"Dryrun: Created specimen(s) {bia_specimen}, but not persisting."
            )
        else:
            store_object_in_api_idempotent(api_client, bia_specimen)

    if not bia_specimen:
        logger.warning("Creating CreationProcess with no Specimen")
    if not image_acquisition_protocol_uuid:
        logger.warning("Creating CreationProcess with no ImageAcquisitionProtocol")
    bia_creation_process = creation_process.get_creation_process(
        study_uuid,
        image_uuid,
        bia_specimen.uuid,
        image_acquisition_protocol_uuid,
    )
    if dryrun:
        logger.info(
            f"Dryrun: Created creation process(es) {bia_creation_process}, but not persisting."
        )
    else:
        store_object_in_api_idempotent(api_client, bia_creation_process)

    bia_image = image.get_image(
        study_uuid,
        submission_dataset_uuid,
        bia_creation_process.uuid,
        file_references=file_references,
    )
    if dryrun:
        logger.info(f"Dryrun: Created Image(s) {bia_image}, but not persisting.")
    else:
        store_object_in_api_idempotent(api_client, bia_image)
        logger.info(
            f"Generated bia_data_model.Image object {bia_image.uuid} and persisted to {api_target} API"
        )
    return str(bia_image.uuid)


@representations_app.command(help="Create specified representations")
def create(
    accession_id: Annotated[str, typer.Argument()],
    image_uuid_list: Annotated[List[str], typer.Argument()],
    api_target: Annotated[
        ApiTarget, typer.Option("--api", "-a", case_sensitive=False)
    ] = ApiTarget.prod,
    dryrun: Annotated[bool, typer.Option()] = False,
    verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False,
) -> None:
    """Create representations for specified file reference(s)"""

    if verbose:
        logger.setLevel(logging.DEBUG)

    api_client = get_api_client(api_target)
    study = api_client.search_study_by_accession(accession_id)
    bia_images = [api_client.get_image(image_uuid) for image_uuid in image_uuid_list]
    for bia_image in bia_images:
        file_references = [
            api_client.get_file_reference(file_reference_uuid)
            for file_reference_uuid in bia_image.original_file_reference_uuid
        ]
        logger.debug(
            f"starting creation of image representation for Image {bia_image.uuid}"
        )
        image_representation = get_image_representation(
            study.uuid,
            file_references,
            bia_image,
            object_creator=semantic_models.Provenance.bia_image_assignment,
        )
        if image_representation:
            message = f"COMPLETED: Creation of image representation {image_representation.uuid} for bia_data_model.Image {bia_image.uuid} of {accession_id}"
            logger.info(message)
            if dryrun:
                logger.info(
                    f"Dryrun: Not persisting image representation:{image_representation}."
                )
            else:
                store_object_in_api_idempotent(api_client, image_representation)
                logger.info(
                    f"Persisted image_representation {image_representation.uuid}"
                )
        else:
            message = f"WARNING: Could NOT create image representation for bia_data_model.Image {bia_image.uuid} of {accession_id}"
            logger.warning(message)


@app.command(help="Assign images from a proposal file")
def assign_from_proposal(
    proposal_path: Annotated[Path, typer.Argument(help="Path to the proposal file")],
    api_target: Annotated[
        ApiTarget, typer.Option("--api", "-a", case_sensitive=False)
    ] = ApiTarget.prod,
    dryrun: Annotated[bool, typer.Option()] = False,
) -> None:
    """Process a proposal file and assign the file references to images"""
    proposals = propose.read_proposals(proposal_path)

    for p in proposals:
        accession_id = p["accession_id"]
        file_reference_uuids = [
            p["file_reference_uuid"],
        ]
        try:
            image_uuid = assign(
                accession_id=accession_id,
                file_reference_uuids=file_reference_uuids,
                api_target=api_target,
                dryrun=dryrun,
            )
        except AssertionError as e:
            logger.error(
                f"Could not assign image for {accession_id} with file reference(s) {file_reference_uuids}. Error was {e}"
            )
            continue

        if not dryrun:
            # Create default representation
            create(
                accession_id=p["accession_id"],
                image_uuid_list=[image_uuid],
                api_target=api_target,
            )


@app.command(help="Propose file references to convert for an accession")
def propose_images(
    accession_ids: Annotated[
        List[str], typer.Argument(help="Accession IDs to process")
    ],
    output_path: Annotated[Path, typer.Argument(help="Path to write the proposals")],
    api_target: Annotated[
        ApiTarget, typer.Option("--api", "-a", case_sensitive=False)
    ] = ApiTarget.prod,
    max_items: Annotated[
        int, typer.Option(help="Maximum number of items to propose")
    ] = 5,
    append: Annotated[
        bool, typer.Option(help="Append to existing file instead of overwriting")
    ] = True,
    check_image_creation_prerequisites: Annotated[
        bool,
        typer.Option(
            help="Check whether dataset linked to file reference contains requirements needed to create a bia_data_model Image object."
        ),
    ] = True,
) -> None:
    """Propose file references to convert for the given accession IDs"""
    for accession_id in accession_ids:
        count = propose.write_convertible_file_references_for_accession_id(
            accession_id,
            output_path,
            api_target=api_target,
            max_items=max_items,
            check_image_creation_prerequisites=check_image_creation_prerequisites,
            append=append,
        )
        logger.info(f"Wrote {count} proposals for {accession_id} to {output_path}")


@app.callback()
def main() -> None:
    return


if __name__ == "__main__":
    app()
