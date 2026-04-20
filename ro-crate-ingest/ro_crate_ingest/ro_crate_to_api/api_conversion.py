import logging
from pathlib import Path

from bia_integrator_api import models
from rich.logging import RichHandler

from bia_ro_crate.core.parser.ro_crate_parser import ROCrateParser
from ro_crate_ingest.ro_crate_to_api.entity_conversion import (
    annotation_method,
    bio_sample,
    dataset,
    file_list,
    image_acquisition_protocol,
    protocol,
    result_data_and_dependency_creation,
    result_data_id_creation,
    specimen_imaging_preparation_protocol,
    study,
)
from ro_crate_ingest.save_utils import PersistenceMode, persist
from ro_crate_ingest.settings import get_settings

logging.basicConfig(
    level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
logger = logging.getLogger()


def convert_ro_crate_to_bia_api(
    crate_path: Path,
    persistence_mode: PersistenceMode,
    file_ref_url_prefix: str | None,
):
    ro_crate_parser = ROCrateParser(crate_path)
    ro_crate_parser.parse()
    parsed_submission_metadata = ro_crate_parser.result

    roc_metadata = parsed_submission_metadata.metadata
    file_list_with_sizes = file_list.prepare_file_list(parsed_submission_metadata.file_list)

    api_objects = []
    api_study = study.create_api_study(roc_metadata.get_object_lookup())
    accession_id = api_study.accession_id
    persist(accession_id, models.Study, [api_study], persistence_mode)
    api_objects.append(study)
    study_uuid = api_study.uuid

    datasets = dataset.create_api_dataset(roc_metadata.get_object_lookup(), study_uuid)
    persist(accession_id, models.Dataset, datasets, persistence_mode)
    api_objects += datasets

    annotation_methods = annotation_method.create_api_image_acquisition_protocol(
        roc_metadata.get_object_lookup(), study_uuid
    )
    persist(accession_id, models.AnnotationMethod, annotation_methods, persistence_mode)
    api_objects += annotation_methods

    protocols = protocol.create_api_protocol(
        roc_metadata.get_object_lookup(), study_uuid
    )
    persist(accession_id, models.Protocol, protocols, persistence_mode)
    api_objects += protocols

    bio_samples = bio_sample.create_api_bio_sample(
        roc_metadata.get_object_lookup(), study_uuid
    )
    persist(accession_id, models.BioSample, bio_samples, persistence_mode)
    api_objects += bio_samples

    image_acquisition_protocols = (
        image_acquisition_protocol.create_api_image_acquisition_protocol(
            roc_metadata.get_object_lookup(), study_uuid
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
        roc_metadata.get_object_lookup(), study_uuid
    )
    persist(
        accession_id,
        models.SpecimenImagingPreparationProtocol,
        specimen_imaging_preparation_protocols,
        persistence_mode,
    )
    api_objects += specimen_imaging_preparation_protocols

    identified_result_data = file_list.process_and_persist_file_references(
        file_list_with_sizes,
        roc_metadata,
        study_uuid,
        accession_id,
        file_ref_url_prefix,
        persistence_mode,
        get_settings().parallelisation_max_workers,
    )

    if not identified_result_data.empty:
        image_dataframe, id_uuid_map = (
            result_data_id_creation.prepare_all_ids_for_result_data(
                identified_result_data,
                roc_metadata.get_object_lookup(),
                study_uuid,
                get_settings().parallelisation_max_workers,
            )
        )

        result_data_and_dependency_creation.create_images_and_dependencies(
            image_dataframe,
            id_uuid_map,
            study_uuid,
            accession_id,
            persistence_mode,
            get_settings().parallelisation_max_workers,
        )
