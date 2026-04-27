import logging
from pathlib import Path
import pandas as pd

from bia_ro_crate.models import ro_crate_models
from bia_ro_crate.models.linked_data.ontology_terms import BIA
from bia_ro_crate.core.bia_ro_crate_metadata import BIAROCrateMetadata
from bia_ro_crate.core.file_list import FileList
from ro_crate_ingest.ro_crate_modification.enrichment.file_list_utils import (
    get_dataset_column_id,
    get_label_column_id,
    get_or_add_associated_annotation_method_column_id,
    get_or_add_associated_source_image_column_id,
    get_or_add_type_column_id,
    get_path_column_id,
)
from ro_crate_ingest.ro_crate_modification.enrichment.utils import (
    FILE_TYPE_ANNOTATION,
    FILE_TYPE_IMAGE,
    refs,
    match_patterns,
    resolve_dataset_id_by_name,
    title_to_id,
    type_for
)
from ro_crate_ingest.ro_crate_modification.modification_config import (
    AnnotationAssignmentConfig,
    DatasetModificationConfig,
    ImageAssignmentConfig
)

logger = logging.getLogger(__name__)

DEFAULT_DATASET_TITLE = "Default dataset"


def _as_scalar_or_list(values: list[str]) -> str | list[str]:
    if len(values) == 1:
        return values[0]
    return values


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

def _build_annotation_label(
    annotation_config: AnnotationAssignmentConfig,
    file_path: str,
) -> str:
    if len(annotation_config.patterns) == 1:
        pattern = annotation_config.patterns[0]
        if "*" not in pattern and "?" not in pattern and "[" not in pattern:
            return Path(pattern).stem
    return Path(file_path).stem


def _apply_annotation_assignment(
    file_list: FileList,
    dataset_rows: pd.DataFrame,
    annotation_config: AnnotationAssignmentConfig,
    *,
    path_col_id: str,
    type_col_id: str,
    label_col_id: str,
    annotation_method_col_id: str,
    associated_source_image_col_id: str,
    dataset_name: str,
) -> int:
    match_mask = dataset_rows[path_col_id].apply(
        lambda p: match_patterns(str(p), annotation_config.patterns)
    )
    matched_rows = dataset_rows[match_mask]
    if matched_rows.empty:
        logger.warning(
            f"Dataset '{dataset_name}': annotation patterns "
            f"{annotation_config.patterns} matched no files."
        )
        return 0

    source_image_values = _as_scalar_or_list(annotation_config.associated_source_image)
    annotation_method_values = [
        title_to_id(title) for title in annotation_config.annotation_method_titles
    ]

    for index, row in matched_rows.iterrows():
        file_path = str(row[path_col_id])
        file_list.data.at[index, type_col_id] = FILE_TYPE_ANNOTATION
        file_list.data.at[index, label_col_id] = _build_annotation_label(
            annotation_config, file_path
        )
        file_list.data.at[index, annotation_method_col_id] = _as_scalar_or_list(
            annotation_method_values
        )
        file_list.data.at[index, associated_source_image_col_id] = source_image_values

    return len(matched_rows)


def assign_annotations_for_dataset(
    file_list: FileList,
    ro_crate_metadata: BIAROCrateMetadata,
    dataset_config: DatasetModificationConfig,
) -> None:
    dataset_id = resolve_dataset_id_by_name(ro_crate_metadata, dataset_config.name)
    if dataset_id is None:
        return

    dataset_col_id = get_dataset_column_id(file_list)
    path_col_id = get_path_column_id(file_list)
    if dataset_col_id is None or path_col_id is None:
        logger.warning(
            f"Dataset '{dataset_config.name}': missing dataset or file path column. "
            "Cannot apply annotation assignment."
        )
        return

    type_col_id = get_or_add_type_column_id(file_list)
    annotation_method_col_id = get_or_add_associated_annotation_method_column_id(file_list)
    associated_source_image_col_id = get_or_add_associated_source_image_column_id(file_list)
    label_col_id = get_label_column_id(file_list)

    required_columns = {
        "label": label_col_id,
    }
    missing_columns = [name for name, col_id in required_columns.items() if col_id is None]
    if missing_columns:
        logger.warning(
            f"Dataset '{dataset_config.name}': missing required file list column(s) "
            f"{missing_columns}. Skipping annotation assignment."
        )
        return

    if file_list.data[label_col_id].dtype != object:
        file_list.data[label_col_id] = file_list.data[label_col_id].astype(object)

    dataset_rows = file_list.data[file_list.data[dataset_col_id] == dataset_id]
    assigned_total = 0
    dataset_entity = ro_crate_metadata.get_object(dataset_id)
    if not isinstance(dataset_entity, ro_crate_models.Dataset):
        logger.warning(
            f"Entity '{dataset_id}' is not a Dataset; cannot apply annotation metadata."
        )
        return

    for annotation_config in dataset_config.annotations:
        assigned_total += _apply_annotation_assignment(
            file_list,
            dataset_rows,
            annotation_config,
            path_col_id=path_col_id,
            type_col_id=type_col_id,
            label_col_id=label_col_id,
            annotation_method_col_id=annotation_method_col_id,
            associated_source_image_col_id=associated_source_image_col_id,
            dataset_name=dataset_config.name,
        )

    annotation_method_titles: list[str] = []
    for annotation_config in dataset_config.annotations:
        for title in annotation_config.annotation_method_titles:
            if title not in annotation_method_titles:
                annotation_method_titles.append(title)

    updated_dataset = dataset_entity.model_copy(update={
        "associatedAnnotationMethod": (
            list(dataset_entity.associatedAnnotationMethod)
            + [
                ref
                for ref in refs(annotation_method_titles)
                if ref not in list(dataset_entity.associatedAnnotationMethod)
            ]
        )
    })
    ro_crate_metadata.update_entity(updated_dataset)

    logger.info(
        f"Dataset '{dataset_config.name}': {assigned_total} file(s) assigned as annotation data."
    )


def assign_image_group_protocols(
    file_list: FileList,
    ro_crate_metadata: BIAROCrateMetadata,
    dataset_config: DatasetModificationConfig,
) -> None:
    """
    For each ImageGroupConfig in dataset_config.image_groups, find the matching
    image files in the dataset and write protocol @id(s) to the
    associated_protocol column in the file list.

    Files must already be assigned to the dataset and marked as images.
    """
    dataset_id = resolve_dataset_id_by_name(ro_crate_metadata, dataset_config.name)
    if dataset_id is None:
        return

    dataset_col_id = get_dataset_column_id(file_list)
    path_col_id = get_path_column_id(file_list)
    type_col_id = get_or_add_type_column_id(file_list)

    if path_col_id is None:
        logger.warning(
            f"Dataset '{dataset_config.name}': no file path column found. "
            "Cannot apply image_groups protocol assignment."
        )
        return

    protocol_col_id = file_list.get_column_id_by_property(str(BIA.associatedProtocol))
    if protocol_col_id is None:
        logger.warning(
            f"Dataset '{dataset_config.name}': no associated_protocol column found in file list; "
            "skipping image_groups protocol assignment."
        )
        return

    if file_list.data[protocol_col_id].dtype != object:
        file_list.data[protocol_col_id] = file_list.data[protocol_col_id].astype(object)

    # Base mask: rows belonging to this dataset and marked as images
    if dataset_col_id is not None:
        dataset_mask = file_list.data[dataset_col_id] == dataset_id
    else:
        dataset_mask = pd.Series(True, index=file_list.data.index)

    if type_col_id is not None:
        image_mask = dataset_mask & (file_list.data[type_col_id] == FILE_TYPE_IMAGE)
    else:
        image_mask = dataset_mask

    dataset_images = file_list.data[image_mask]

    for group in dataset_config.image_groups:
        group_mask = dataset_images[path_col_id].apply(
            lambda p: match_patterns(str(p), group.patterns)
        )
        matched_indices = dataset_images[group_mask].index

        if matched_indices.empty:
            logger.warning(
                f"Dataset '{dataset_config.name}': image_groups patterns "
                f"{group.patterns} matched no image files."
            )
            continue

        ids = [title_to_id(t) for t in group.protocol_titles]
        value = str(ids) if len(ids) > 1 else ids[0]
        file_list.data.loc[matched_indices, protocol_col_id] = value

        logger.debug(
            f"Dataset '{dataset_config.name}': wrote protocol(s) {ids} "
            f"to {len(matched_indices)} file(s) via image_groups."
        )


def assign_additional_files_for_dataset(
    file_list: FileList,
    ro_crate_metadata: BIAROCrateMetadata,
    dataset_config: DatasetModificationConfig,
) -> None:
    """
    Assign currently-unassigned files to an existing named dataset, with
    optional image marking (including typed image assignment for specimen
    track participation).

    Only files with no existing dataset assignment are considered. The search
    pool is first narrowed by data_directories (if given), then optionally
    filtered by patterns. Within the matched set, each AdditionalFileImageAssignment
    entry marks a subset as images, with an optional image type recorded in the
    file list for later use by specimen track identification.
    """
    dataset_id = resolve_dataset_id_by_name(ro_crate_metadata, dataset_config.name)
    if dataset_id is None:
        return

    dataset_col_id = get_dataset_column_id(file_list)
    path_col_id = get_path_column_id(file_list)

    if path_col_id is None:
        logger.warning(
            f"Dataset '{dataset_config.name}': no file path column found. "
            "Cannot apply additional_files assignment."
        )
        return

    additional = dataset_config.additional_files

    # Pool: rows with no existing dataset assignment
    if dataset_col_id is not None:
        unassigned_mask = file_list.data[dataset_col_id].isna()
    else:
        unassigned_mask = pd.Series(True, index=file_list.data.index)

    candidate_rows = file_list.data[unassigned_mask]

    # Narrow by data_directories if given (any path that falls under any listed directory)
    if additional.data_directories:
        dir_mask = candidate_rows[path_col_id].apply(
            lambda p: match_patterns(str(p), [
                f"{d.rstrip('/')}/**" for d in additional.data_directories
            ])
        )
        candidate_rows = candidate_rows[dir_mask]

    # Further filter by patterns if given
    if additional.patterns:
        pattern_mask = candidate_rows[path_col_id].apply(
            lambda p: match_patterns(str(p), additional.patterns)
        )
        candidate_rows = candidate_rows[pattern_mask]

    if candidate_rows.empty:
        logger.warning(
            f"Dataset '{dataset_config.name}': additional_files matched no unassigned files."
        )
        return

    # Assign matched files to this dataset
    if dataset_col_id is not None:
        file_list.data.loc[candidate_rows.index, dataset_col_id] = dataset_id

    logger.info(
        f"Dataset '{dataset_config.name}': {len(candidate_rows)} unassigned file(s) "
        "assigned via additional_files."
    )

    # Mark images within the newly-assigned files
    if not additional.images:
        return

    type_col_id = get_or_add_type_column_id(file_list)

    for img_assignment in additional.images:
        img_mask = candidate_rows[path_col_id].apply(
            lambda p: match_patterns(str(p), img_assignment.patterns)
        )
        matched_indices = candidate_rows[img_mask].index

        if matched_indices.empty:
            logger.warning(
                f"Dataset '{dataset_config.name}': additional_files image patterns "
                f"{img_assignment.patterns} matched no files."
            )
            continue

        file_list.data.loc[matched_indices, type_col_id] = FILE_TYPE_IMAGE
        logger.debug(
            f"Dataset '{dataset_config.name}': {len(matched_indices)} additional file(s) "
            f"marked as image(s) with image_type={img_assignment.image_type!r}."
        )


def assign_unassigned_to_default_dataset(
    file_list: FileList,
    ro_crate_metadata: BIAROCrateMetadata,
) -> None:
    """
    After all named dataset enrichment is complete, collect any files that
    remain unassigned and place them in a new 'Default dataset' entity.

    The default dataset entity is only created if there are actually unassigned
    files — if everything has been accounted for, nothing is written.
    """
    dataset_col_id = get_dataset_column_id(file_list)

    if dataset_col_id is None:
        logger.debug(
            "No dataset membership column found; cannot create default dataset."
        )
        return

    unassigned_mask = file_list.data[dataset_col_id].isna()
    unassigned_count = int(unassigned_mask.sum())

    if unassigned_count == 0:
        logger.debug("All files are assigned to a dataset; no default dataset needed.")
        return

    # Guard against the entity already existing (e.g. idempotency re-runs)
    default_dataset_id = title_to_id(DEFAULT_DATASET_TITLE)
    if ro_crate_metadata.get_object(default_dataset_id) is not None:
        logger.warning(
            f"Default dataset entity '{default_dataset_id}' already exists; "
            "skipping creation but still assigning unassigned files to it."
        )
    else:
        default_dataset = ro_crate_models.Dataset(
            **{"@id": default_dataset_id, 
               "@type": ["Dataset", type_for(ro_crate_models.Dataset)], 
               "name": DEFAULT_DATASET_TITLE}
        )
        ro_crate_metadata.add_entity(default_dataset)
        logger.info(f"Created default dataset entity: {default_dataset_id}")

    file_list.data.loc[unassigned_mask, dataset_col_id] = default_dataset_id
    logger.info(
        f"Default dataset: {unassigned_count} unassigned file(s) assigned to "
        f"'{DEFAULT_DATASET_TITLE}'."
    )
