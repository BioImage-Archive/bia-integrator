import logging
from ro_crate_ingest.crate_reader import (
    process_ro_crate,
    load_ro_crate_metadata_to_graph,
)
from ro_crate_ingest.ro_crate_to_api.entity_conversion import (
    annotation_method,
    bio_sample,
    dataset,
    image_acquisition_protocol,
    protocol,
    specimen_imaging_preparation_protocol,
    study,

    dataframe_assembly,
    dataframe_file_reference,
    dataframe_image_prerequisites,
    dataframe_image_and_dependencies,
)
from pathlib import Path
from rich.logging import RichHandler
from ..save_utils import PersistenceMode, persist
from bia_integrator_api import models
from ro_crate_ingest.settings import get_settings



logging.basicConfig(
    level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
logger = logging.getLogger()


def convert_ro_crate_to_bia_api(
    crate_path: Path,
    persistence_mode: PersistenceMode,
    file_ref_url_prefix: str,
):
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

    file_dataframe = dataframe_assembly.create_combined_file_dataframe(
        entities, crate_path, crate_graph
    )

    image_raw_dataframe = dataframe_file_reference.process_and_persist_file_references(
        file_dataframe,
        study_uuid,
        accession_id,
        file_ref_url_prefix,
        persistence_mode,
        get_settings().parallelisation_max_workers,
    )

    if not image_raw_dataframe["image_id"].isna().all():
        image_dataframe, id_uuid_map = (
            dataframe_image_prerequisites.prepare_all_ids_for_images(
                image_raw_dataframe, entities, study_uuid
            )
        )
        dataframe_image_and_dependencies.create_images_and_dependencies(
            image_dataframe,
            entities,
            id_uuid_map,
            study_uuid,
            accession_id,
            persistence_mode,
            get_settings().parallelisation_max_workers,
        )
