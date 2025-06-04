import typer
import logging
from typing import Annotated, Optional
from ro_crate_ingest.crate_reader import process_ro_crate
from ro_crate_ingest.entity_conversion import (
    AnnotationMethod,
    BioSample,
    Dataset,
    ImageAcquisitionProtocol,
    Protocol,
    SpecimenImagingPreparationProtocol,
    Study,
    FileReference,
    Image,
)
from pathlib import Path
from rich.logging import RichHandler
from .save_utils import PersistenceMode, persist
from bia_integrator_api import models

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
            "--persistance-mode",
            "-p",
            case_sensitive=False,
            help="Mode to persist the data. Options: local_file, local_api, bia_api",
        ),
    ] = PersistenceMode.LOCAL_FILE,
):

    entities = process_ro_crate(crate_path)

    api_objects = []

    study = Study.create_api_study(entities)
    accession_id = study.accession_id
    persist(accession_id, models.Study, [study], persistence_mode)
    api_objects.append(study)
    study_uuid = study.uuid

    datasets = Dataset.create_api_dataset(entities, study_uuid)
    persist(accession_id, models.Dataset, datasets, persistence_mode)
    api_objects += datasets

    annotation_methods = AnnotationMethod.create_api_image_acquisition_protocol(
        entities, study_uuid
    )
    persist(accession_id, models.AnnotationMethod, annotation_methods, persistence_mode)
    api_objects += annotation_methods

    protocols = Protocol.create_api_protocol(entities, study_uuid)
    persist(accession_id, models.Protocol, protocols, persistence_mode)
    api_objects += protocols

    bio_samples = BioSample.create_api_bio_sample(entities, study_uuid)
    persist(accession_id, models.BioSample, bio_samples, persistence_mode)
    api_objects += bio_samples

    image_acquisition_protocols = (
        ImageAcquisitionProtocol.create_api_image_acquisition_protocol(
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

    specimen_imaging_preparation_protocols = SpecimenImagingPreparationProtocol.create_api_specimen_imaging_preparation_protocol(
        entities, study_uuid
    )
    persist(
        accession_id,
        models.SpecimenImagingPreparationProtocol,
        specimen_imaging_preparation_protocols,
        persistence_mode,
    )
    api_objects += specimen_imaging_preparation_protocols

    # TODO: Handle dependency tree for images and creation processes, expecially when annotation images are explicitly included, but original images are not.
    image_file_refs, creation_processes, images = Image.create_image_and_dependencies(
        entities, study_uuid, crate_path
    )

    file_references = FileReference.create_file_reference(
        entities, study_uuid, crate_path
    )
    persist(accession_id, models.FileReference, file_references, persistence_mode)
    api_objects += file_references
