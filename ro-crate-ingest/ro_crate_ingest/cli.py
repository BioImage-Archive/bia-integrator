import typer
import logging
from typing import Annotated, Optional
from ro_crate_ingest.crate_reader import process_ro_crate
from ro_crate_ingest.entity_conversion import (
    dataset,
    image_acquisition_protocol,
    protocol,
    study,
    image,
    specimen,
    annotation_method,
    bio_sample,
    file_reference,
    specimen_imaging_preparation_protocol,
)
from ro_crate_ingest.entity_conversion.file_list import process_file_lists
from pathlib import Path
from rich.logging import RichHandler
from .save_utils import PersistenceMode, persist, persist_in_order
from bia_integrator_api import models
from ro_crate_ingest.crate_reader import load_ro_crate_metadata_to_graph

ro_crate_ingest = typer.Typer()

logging.basicConfig(
    level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
logger = logging.getLogger()


@ro_crate_ingest.command("ingest")
def convert(
    crate_path: Annotated[
        Optional[Path],
        typer.Option(
            "--crate-path",
            "-c",
            case_sensitive=False,
            help="Path to the ro-crate root (or ro-crate-metadata.json)",
        ),
    ] = None,
    persistence_mode: Annotated[
        Optional[PersistenceMode],
        typer.Option(
            "--persistence-mode",
            "-p",
            case_sensitive=False,
            help="Mode to persist the data. Options: local_file, local_api, bia_api",
        ),
    ] = PersistenceMode.LOCAL_FILE,
):

    crate_path = crate_path.resolve()
    if crate_path.name == "ro-crate-metadata.json":
        crate_path = crate_path.parent

    entities = process_ro_crate(crate_path)
    crate_graph = load_ro_crate_metadata_to_graph(crate_path)

    api_objects = []
    api_study = study.create_api_study(entities)
    accession_id = api_study.accession_id
    persist(accession_id, models.Study, [api_study], persistence_mode)
    api_objects.append(study)
    study_uuid = api_study.uuid

    datasets = dataset.create_api_dataset(entities, study_uuid)
    persist(accession_id, models.Dataset, datasets, persistence_mode)
    api_objects += datasets

    annotation_methods = annotation_method.create_api_image_acquisition_protocol(
        entities, study_uuid
    )
    persist(accession_id, models.AnnotationMethod, annotation_methods, persistence_mode)
    api_objects += annotation_methods

    protocols = protocol.create_api_protocol(entities, study_uuid)
    persist(accession_id, models.Protocol, protocols, persistence_mode)
    api_objects += protocols

    bio_samples = bio_sample.create_api_bio_sample(entities, study_uuid)
    persist(accession_id, models.BioSample, bio_samples, persistence_mode)
    api_objects += bio_samples

    image_acquisition_protocols = (
        image_acquisition_protocol.create_api_image_acquisition_protocol(
            entities, study_uuid
        )
    )
    persist(
        accession_id,
        models.ImageAcquisitionProtocol,
        image_acquisition_protocols,
        persistence_mode,
    )
    api_objects += image_acquisition_protocols

    specimen_imaging_preparation_protocols = specimen_imaging_preparation_protocol.create_api_specimen_imaging_preparation_protocol(
        entities, study_uuid
    )
    persist(
        accession_id,
        models.SpecimenImagingPreparationProtocol,
        specimen_imaging_preparation_protocols,
        persistence_mode,
    )
    api_objects += specimen_imaging_preparation_protocols

    specimens = specimen.create_api_specimen(entities, study_uuid)
    api_objects += specimens
    persist(accession_id, models.Specimen, specimens, persistence_mode)

    processed_file_paths = []
    # TODO: Handle dependency tree for images and creation processes, expecially when annotation images are explicitly included, but original images are not.
    (
        image_file_refs,
        file_paths,
        ordered_images_and_creation_processes,
        max_chain_length,
    ) = image.create_image_and_dependencies(
        entities, study_uuid, crate_path, crate_graph
    )
    persist(accession_id, models.FileReference, image_file_refs, persistence_mode)
    api_objects += image_file_refs
    processed_file_paths += file_paths
    persist_in_order(
        ordered_images_and_creation_processes,
        max_chain_length,
        persistence_mode,
        accession_id,
    )

    file_list_file_refs, file_paths = process_file_lists(
        entities, crate_path, crate_graph, study_uuid
    )
    persist(accession_id, models.FileReference, file_list_file_refs, persistence_mode)
    api_objects += file_list_file_refs
    processed_file_paths += file_paths

    # TODO: don't create file references again for files that are already created with images
    file_references = file_reference.create_file_reference(
        entities, study_uuid, crate_path, processed_file_paths
    )
    persist(accession_id, models.FileReference, file_references, persistence_mode)
    api_objects += file_references
