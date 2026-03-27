import logging

from ro_crate_ingest.bia_ro_crate.bia_ro_crate_metadata import BIAROCrateMetadata
from ro_crate_ingest.bia_ro_crate.file_list import FileList
from ro_crate_ingest.ro_crate_modification.modification_config import (
    DEFAULT_DATASET_SENTINEL,
    ModificationConfig,
)
from ro_crate_ingest.ro_crate_modification.enrichment import (
    images, 
    rembis, 
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

    1. Add study-wide REMBI entities to the metadata graph.
    2. For each named dataset: apply image assignment and explicit associations.
    3. Create the default dataset and assign its images (if sentinel present).
    4. Identify and assign specimen tracks (if specimen_tracks configured).

    Returns the modified (ro_crate_metadata, file_list) pair.
    """
    if config.rembis:
        rembis.add_rembi_entities(ro_crate_metadata, config.rembis)

    named_configs = [d for d in config.datasets if d.name != DEFAULT_DATASET_SENTINEL]
    default_config = next(
        (d for d in config.datasets if d.name == DEFAULT_DATASET_SENTINEL), None
    )

    for dataset_config in named_configs:
        if dataset_config.associations:
            rembis.apply_dataset_associations(ro_crate_metadata, dataset_config)
        if dataset_config.images:
            images.assign_images_for_dataset(file_list, ro_crate_metadata, dataset_config)

    if default_config is not None and default_config.images:
        images.assign_images_for_default_dataset(file_list, ro_crate_metadata, default_config)

    if config.specimen_tracks:
        specimens.assign_specimen_tracks(ro_crate_metadata, file_list, config)

    return ro_crate_metadata, file_list
