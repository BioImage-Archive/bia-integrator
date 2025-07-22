from typing import List
from pathlib import Path
from typing import Annotated
import typer
from bia_shared_datamodels import uuid_creation, semantic_models
from bia_assign_image import propose
from bia_assign_image.object_creation import (
    image,
    image_representation,
)
from bia_assign_image.api_client import (
    ApiTarget,
    get_api_client,
    store_object_in_api_idempotent,
)
import logging
from bia_assign_image.image_assignment import (
    find_exisiting_image_dependencies,
    create_missing_dependencies,
    ImageDependencies,
)
from bia_shared_datamodels.package_specific_uuid_creation import shared


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


@app.command(help="Assign listed file references to an image")
def assign(
    accession_id: Annotated[str, typer.Argument()],
    file_reference_uuids: Annotated[List[str], typer.Argument()],
    api_target: Annotated[
        ApiTarget, typer.Option("--api", "-a", case_sensitive=False)
    ] = ApiTarget.prod,
    pattern: Annotated[
        str | None, typer.Option("--pattern", "-p", case_sensitive=False)
    ] = None,
    dryrun: Annotated[bool, typer.Option()] = False,
) -> str:
    api_client = get_api_client(api_target)

    # Get / Create relevant uuids that will be used for missing dependency creation
    study_uuid = uuid_creation.create_study_uuid(accession_id)

    image_uuid, image_uuid_attribute = shared.create_image_uuid(
        study_uuid,
        file_reference_uuids,
        semantic_models.Provenance.bia_image_assignment,
    )

    file_references = [api_client.get_file_reference(f) for f in file_reference_uuids]

    image_dependencies: ImageDependencies = find_exisiting_image_dependencies(
        file_references, api_client
    )
    image_dependencies = create_missing_dependencies(
        study_uuid, image_uuid, image_dependencies, api_client, dryrun
    )

    assert image_dependencies.has_dependencies_for_image_creation()
    bia_image = image.get_image(
        image_uuid,
        image_uuid_attribute,
        image_dependencies.dataset_uuid,
        image_dependencies.creation_process_uuid,
        file_references,
        pattern,
    )
    if dryrun:
        logger.info(f"Dryrun: Created Image(s) {bia_image}, but not persisting.")
    else:
        store_object_in_api_idempotent(api_client, bia_image)
        logger.info(
            f"Generated bia_data_model.Image object {bia_image.uuid} and persisted to {api_target} API"
        )

    if not dryrun:
        # Create default representation
        create(
            accession_id=accession_id,
            image_uuid_list=[
                f"{bia_image.uuid}",
            ],
            api_target=api_target,
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
        image_rep = image_representation.get_image_representation(
            study.uuid,
            file_references,
            bia_image,
            object_creator=semantic_models.Provenance.bia_image_assignment,
        )
        if image_rep:
            message = f"COMPLETED: Creation of image representation {image_rep.uuid} for bia_data_model.Image {bia_image.uuid} of {accession_id}"
            logger.info(message)
            if dryrun:
                logger.info(f"Dryrun: Not persisting image representation:{image_rep}.")
            else:
                store_object_in_api_idempotent(api_client, image_rep)
                logger.info(f"Persisted image_representation {image_rep.uuid}")
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
        file_reference_uuids = p["file_reference_uuid"].split(" ")
        pattern = p.get("pattern", None)
        try:
            assign(
                accession_id=accession_id,
                file_reference_uuids=file_reference_uuids,
                api_target=api_target,
                pattern=pattern,
                dryrun=dryrun,
            )
        except AssertionError as e:
            logger.error(
                f"Could not assign image for {accession_id} with file reference(s) {file_reference_uuids}. Error was {e}"
            )
            continue


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


@app.command(
    help="Propose file references for source images and associated annotations to convert for an accession"
)
def propose_images_and_annotations(
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
    ] = False,
) -> None:
    """Propose file references for source images and associated annotations to convert for an accession IDs"""
    for accession_id in accession_ids:
        n_source_images, n_annotations = (
            propose.write_convertible_source_annotation_file_refs_for_acc_id(
                accession_id,
                output_path,
                api_target=api_target,
                max_items=max_items,
                check_image_creation_prerequisites=check_image_creation_prerequisites,
                append=append,
            )
        )
        logger.info(
            f"Wrote {n_source_images} source image proposals and {n_annotations} annotation image proposals for {accession_id} to {output_path}"
        )


@app.callback()
def main() -> None:
    return


if __name__ == "__main__":
    app()
