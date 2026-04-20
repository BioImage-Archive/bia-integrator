import logging

from bia_ro_crate.core.bia_ro_crate_metadata import BIAROCrateMetadata
from bia_ro_crate.core.file_list import FileList
from ro_crate_ingest.ro_crate_modification.modification_config import ModificationConfig
from ro_crate_ingest.ro_crate_modification.enrichment import (
    assignments,
    rembis,
    study,
    specimens
)

logger = logging.getLogger(__name__)


def apply_enrichment(
    ro_crate_metadata: BIAROCrateMetadata,
    file_list: FileList,
    config: ModificationConfig,
) -> tuple[BIAROCrateMetadata, FileList]:
    """
    Apply all enrichment steps to a minimal RO-Crate in the order:

    1. Add information to the study object.
    2. Add study-wide REMBI entities to the metadata graph.
    3. For each named dataset:
       a. Apply explicit REMBI associations.
       b. Assign additional unassigned files to the dataset (with optional
          image marking, including typed images for specimen tracks).
       c. Apply image assignment for files already in the dataset.
       d. Write image-group protocol associations.
    4. Identify and assign specimen tracks (if specimen_tracks configured).
    5. Create the default dataset and assign any remaining unassigned files.

    The default dataset is created automatically — no YAML entry is needed.

    Returns the modified (ro_crate_metadata, file_list) pair.
    """
    if config.study_metadata:
        study.add_study_metadata(ro_crate_metadata, config.study_metadata)

    if config.rembis:
        rembis.add_rembi_entities(ro_crate_metadata, config.rembis)

    for dataset_config in config.datasets:
        if dataset_config.associations:
            rembis.apply_dataset_associations(ro_crate_metadata, dataset_config)

        if dataset_config.additional_files:
            assignments.assign_additional_files_for_dataset(
                file_list, ro_crate_metadata, dataset_config
            )

        if dataset_config.images:
            assignments.assign_images_for_dataset(file_list, ro_crate_metadata, dataset_config)

        if dataset_config.image_groups:
            assignments.assign_image_group_protocols(
                file_list, ro_crate_metadata, dataset_config
            )

    if config.specimen_tracks:
        specimens.assign_specimen_tracks(ro_crate_metadata, file_list, config)

    assignments.assign_unassigned_to_default_dataset(file_list, ro_crate_metadata)

    return ro_crate_metadata, file_list
