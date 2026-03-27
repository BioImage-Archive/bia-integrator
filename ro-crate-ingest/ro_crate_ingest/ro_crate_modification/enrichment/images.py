import logging
import pandas as pd

from bia_shared_datamodels import ro_crate_models
from ro_crate_ingest.bia_ro_crate.bia_ro_crate_metadata import BIAROCrateMetadata
from ro_crate_ingest.bia_ro_crate.file_list import FileList
from ro_crate_ingest.ro_crate_modification.enrichment.utils import (
    FILE_TYPE_IMAGE, 
    get_dataset_column_id, 
    get_or_add_type_column_id, 
    get_path_column_id, 
    match_patterns, 
    resolve_dataset_id_by_name, 
    title_to_id
)
from ro_crate_ingest.ro_crate_modification.modification_config import (
    DEFAULT_DATASET_TITLE,
    DatasetModificationConfig,
    ImageAssignmentConfig,
)

logger = logging.getLogger(__name__)


def _apply_image_assignment(
    file_list: FileList,
    images_config: ImageAssignmentConfig,
    row_mask: pd.Series,
    type_col_id: str,
    dataset_name: str,
) -> int:
    """
    Apply glob pattern matching to rows selected by row_mask, writing
    FILE_TYPE_IMAGE into type_col_id for each match. Returns count assigned.

    Both flat (patterns) and keyed (by_type) forms write FILE_TYPE_IMAGE —
    the by_type key distinction is used only during specimen track
    identification, not written to the file list.
    """
    path_col_id = get_path_column_id(file_list)
    if path_col_id is None:
        logger.warning(
            f"Dataset '{dataset_name}': no file path column found. "
            "Cannot apply image assignment."
        )
        return 0

    all_patterns: list[str] = []
    if images_config.patterns:
        all_patterns = images_config.patterns
    else:
        for raw_patterns in images_config.by_type.values():
            if isinstance(raw_patterns, str):
                all_patterns.append(raw_patterns)
            else:
                all_patterns.extend(raw_patterns)

    candidate_rows = file_list.data[row_mask]
    match_mask = candidate_rows[path_col_id].apply(
        lambda p: match_patterns(str(p), all_patterns)
    )
    matched_indices = candidate_rows[match_mask].index
    file_list.data.loc[matched_indices, type_col_id] = FILE_TYPE_IMAGE

    count = int(match_mask.sum())
    if count == 0:
        logger.warning(f"Dataset '{dataset_name}': image patterns matched no files.")
    else:
        logger.debug(
            f"Dataset '{dataset_name}': {count} file(s) assigned as {FILE_TYPE_IMAGE}."
        )
    return count


def assign_images_for_dataset(
    file_list: FileList,
    ro_crate_metadata: BIAROCrateMetadata,
    dataset_config: DatasetModificationConfig,
) -> None:
    dataset_id = resolve_dataset_id_by_name(ro_crate_metadata, dataset_config.name)
    if dataset_id is None:
        return

    dataset_col_id = get_dataset_column_id(file_list)
    if dataset_col_id is None:
        logger.warning(
            f"Dataset '{dataset_config.name}': no dataset membership column found. Skipping."
        )
        return

    type_col_id = get_or_add_type_column_id(file_list)
    dataset_mask = file_list.data[dataset_col_id] == dataset_id
    assigned = _apply_image_assignment(
        file_list, dataset_config.images, dataset_mask, type_col_id, dataset_config.name
    )
    logger.info(
        f"Dataset '{dataset_config.name}': {assigned} file(s) assigned as image(s)."
    )


def _make_default_dataset_entity(
    ro_crate_metadata: BIAROCrateMetadata,
) -> ro_crate_models.Dataset:
    dataset_id = title_to_id(DEFAULT_DATASET_TITLE)
    if ro_crate_metadata.get_object(dataset_id) is not None:
        raise ValueError(
            f"Cannot create default dataset: entity '{dataset_id}' already exists."
        )
    return ro_crate_models.Dataset(**{"@id": dataset_id, "name": DEFAULT_DATASET_TITLE})


def assign_images_for_default_dataset(
    file_list: FileList,
    ro_crate_metadata: BIAROCrateMetadata,
    default_config: DatasetModificationConfig,
) -> None:
    type_col_id = get_or_add_type_column_id(file_list)
    dataset_col_id = get_dataset_column_id(file_list)

    if dataset_col_id is not None:
        unassigned_mask = file_list.data[dataset_col_id].isna()
    else:
        unassigned_mask = pd.Series(True, index=file_list.data.index)

    assigned = _apply_image_assignment(
        file_list, default_config.images, unassigned_mask, type_col_id, DEFAULT_DATASET_TITLE
    )

    if assigned == 0:
        logger.info("Default dataset: no files matched; skipping entity creation.")
        return

    default_dataset_entity = _make_default_dataset_entity(ro_crate_metadata)
    ro_crate_metadata.add_entity(default_dataset_entity)
    logger.info(f"Created default dataset entity: {default_dataset_entity.id}")

    if dataset_col_id is not None:
        matched_mask = unassigned_mask & (file_list.data[type_col_id] == FILE_TYPE_IMAGE)
        file_list.data.loc[matched_mask, dataset_col_id] = default_dataset_entity.id

    logger.info(f"Default dataset: {assigned} file(s) assigned as image(s).")