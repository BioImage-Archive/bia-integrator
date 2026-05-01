import logging
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from bia_ro_crate.models import ro_crate_models
from bia_ro_crate.core.bia_ro_crate_metadata import BIAROCrateMetadata
from bia_ro_crate.core.file_list import FileList
from ro_crate_ingest.ro_crate_modification.enrichment.file_list_utils import (
    file_list_association_value,
    get_dataset_column_id,
    get_or_add_associated_annotation_method_column_id,
    get_or_add_associated_protocol_column_id,
    get_or_add_associated_source_image_column_id,
    get_or_add_label_column_id,
    get_or_add_type_column_id,
    get_path_column_id,
)
from ro_crate_ingest.ro_crate_modification.enrichment.utils import (
    FILE_TYPE_ANNOTATION,
    FILE_TYPE_IMAGE,
    entity_ref,
    entity_refs,
    match_patterns,
    resolve_dataset_id_by_name,
    title_to_id,
    type_for,
)
from ro_crate_ingest.ro_crate_modification.modification_config import (
    AnnotationAssignmentConfig,
    DatasetModificationConfig,
    ImageGroupConfig,
    ImageAssignmentConfig,
)

logger = logging.getLogger(__name__)

DEFAULT_DATASET_TITLE = "Default dataset"
MAX_WARNING_PATHS = 5


@dataclass(frozen=True)
class ResultAssignmentContext:
    file_list: FileList
    dataset_name: str
    dataset_id: str
    dataset_col_id: str
    path_col_id: str
    type_col_id: str

    @property
    def dataset_rows(self) -> pd.DataFrame:
        return self.file_list.data[
            self.file_list.data[self.dataset_col_id] == self.dataset_id
        ]


def _require_columns(
    dataset_name: str,
    assignment_name: str,
    columns: dict[str, str | None],
) -> bool:
    missing_columns = [name for name, col_id in columns.items() if col_id is None]
    if not missing_columns:
        return True

    logger.warning(
        f"Dataset '{dataset_name}': missing required file list column(s) "
        f"{missing_columns}. Skipping {assignment_name}."
    )
    return False


def _patterns_from_image_config(images_config: ImageAssignmentConfig) -> list[str]:
    if images_config.patterns:
        return images_config.patterns

    all_patterns: list[str] = []
    for raw_patterns in images_config.by_type.values():
        if isinstance(raw_patterns, str):
            all_patterns.append(raw_patterns)
        else:
            all_patterns.extend(raw_patterns)
    return all_patterns


def _matching_rows(
    assignment_context: ResultAssignmentContext,
    patterns: list[str],
    rows: pd.DataFrame | None = None,
) -> pd.DataFrame:
    if rows is None:
        rows = assignment_context.dataset_rows

    path_col_id = assignment_context.path_col_id
    match_mask = rows[path_col_id].apply(
        lambda path: match_patterns(str(path), patterns)
    )
    return rows[match_mask]


def _warn_before_overwriting_values(
    assignment_context: ResultAssignmentContext,
    row_indices: pd.Index,
    column_id: str,
    new_value: str | list[str],
    assignment_name: str,
    value_name: str,
) -> None:
    file_list = assignment_context.file_list

    conflicting_indices = []
    for index in row_indices:
        existing_value = file_list.data.at[index, column_id]
        has_value = (
            bool(existing_value)
            if isinstance(existing_value, list)
            else pd.notna(existing_value)
        )
        if has_value and existing_value != new_value:
            conflicting_indices.append(index)

    if not conflicting_indices:
        return

    paths = (
        file_list.data.loc[conflicting_indices, assignment_context.path_col_id]
        .astype(str)
        .tolist()
    )
    shown_paths = ", ".join(paths[:MAX_WARNING_PATHS])
    if len(paths) > MAX_WARNING_PATHS:
        shown_paths += ", ..."

    logger.warning(
        f"Dataset '{assignment_context.dataset_name}': {assignment_name} overwriting existing "
        f"{value_name} for {len(conflicting_indices)} file(s): {shown_paths}."
    )


def _apply_result_assignment(
    assignment_context: ResultAssignmentContext,
    assignment_name: str,
    patterns: list[str],
    result_type: str,
    label_col_id: str | None = None,
    label_builder: Callable[[str], str] | None = None,
    extra_column_values: dict[str, str | list[str]] | None = None,
) -> int:
    """
    Shared pattern-based assignment for dataset result objects.

    Image and annotation assignments differ in the result type and associated
    metadata they write, but share the mechanics of matching files, writing the
    type column, and warning when a later assignment overwrites earlier values.
    """
    matched_rows = _matching_rows(
        assignment_context=assignment_context,
        patterns=patterns,
    )
    if matched_rows.empty:
        logger.warning(
            f"Dataset '{assignment_context.dataset_name}': {assignment_name} patterns "
            f"{patterns} matched no files."
        )
        return 0

    matched_indices = matched_rows.index
    _warn_before_overwriting_values(
        assignment_context=assignment_context,
        row_indices=matched_indices,
        column_id=assignment_context.type_col_id,
        new_value=result_type,
        assignment_name=assignment_name,
        value_name="type",
    )
    assignment_context.file_list.data.loc[
        matched_indices, assignment_context.type_col_id
    ] = result_type

    if label_col_id is not None and label_builder is not None:
        for index, row in matched_rows.iterrows():
            file_path = str(row[assignment_context.path_col_id])
            new_label = label_builder(file_path)
            _warn_before_overwriting_values(
                assignment_context=assignment_context,
                row_indices=pd.Index([index]),
                column_id=label_col_id,
                new_value=new_label,
                assignment_name=assignment_name,
                value_name="label",
            )
            assignment_context.file_list.data.at[index, label_col_id] = new_label

    if extra_column_values:
        for col_id, value in extra_column_values.items():
            _warn_before_overwriting_values(
                assignment_context=assignment_context,
                row_indices=matched_indices,
                column_id=col_id,
                new_value=value,
                assignment_name=assignment_name,
                value_name=assignment_context.file_list.schema[col_id].columnName,
            )
            for index in matched_indices:
                assignment_context.file_list.data.at[index, col_id] = value

    return len(matched_rows)


def _assign_image_group_protocols(
    assignment_context: ResultAssignmentContext,
    image_groups: list[ImageGroupConfig],
) -> None:
    """
    For each ImageGroupConfig, find matching image files in the dataset and
    write protocol @id(s) to the associated_protocol column in the file list.

    Files must already be assigned to the dataset and marked as images.
    """
    protocol_col_id = get_or_add_associated_protocol_column_id(
        assignment_context.file_list
    )

    dataset_rows = assignment_context.dataset_rows
    image_mask = dataset_rows[assignment_context.type_col_id] == FILE_TYPE_IMAGE
    dataset_images = dataset_rows[image_mask]

    for group in image_groups:
        matched_indices = _matching_rows(
            assignment_context=assignment_context,
            patterns=group.patterns,
            rows=dataset_images,
        )
        matched_indices = matched_indices.index

        if matched_indices.empty:
            logger.warning(
                f"Dataset '{assignment_context.dataset_name}': image_groups patterns "
                f"{group.patterns} matched no image files."
            )
            continue

        ids = [title_to_id(t) for t in group.protocol_titles]
        value = file_list_association_value(ids)
        _warn_before_overwriting_values(
            assignment_context=assignment_context,
            row_indices=matched_indices,
            column_id=protocol_col_id,
            new_value=value,
            assignment_name="image_groups protocol assignment",
            value_name="associated_protocol",
        )
        assignment_context.file_list.data.loc[matched_indices, protocol_col_id] = value

        logger.debug(
            f"Dataset '{assignment_context.dataset_name}': wrote protocol(s) {ids} "
            f"to {len(matched_indices)} file(s) via image_groups."
        )


def _ensure_object_columns(file_list: FileList, column_ids: list[str]) -> None:
    for col_id in column_ids:
        if file_list.data[col_id].dtype != object:
            file_list.data[col_id] = file_list.data[col_id].astype(object)


def _build_annotation_label(
    annotation_config: AnnotationAssignmentConfig,
    file_path: str,
) -> str:
    if len(annotation_config.patterns) == 1:
        pattern = annotation_config.patterns[0]
        if "*" not in pattern and "?" not in pattern and "[" not in pattern:
            return Path(pattern).stem
    return Path(file_path).stem


def _update_dataset_annotation_methods(
    ro_crate_metadata: BIAROCrateMetadata,
    dataset_id: str,
    annotation_configs: list[AnnotationAssignmentConfig],
) -> None:
    dataset_entity = ro_crate_metadata.get_object(dataset_id)

    titles: list[str] = []
    for annotation_config in annotation_configs:
        for title in annotation_config.annotation_method_titles:
            if title not in titles:
                titles.append(title)

    existing_refs = list(dataset_entity.associatedAnnotationMethod)
    updated_dataset = dataset_entity.model_copy(
        update={
            "associatedAnnotationMethod": existing_refs
            + [
                new_ref
                for new_ref in entity_refs(titles)
                if new_ref not in existing_refs
            ]
        }
    )
    ro_crate_metadata.update_entity(updated_dataset)


def _add_default_dataset_to_study_has_part(
    ro_crate_metadata: BIAROCrateMetadata,
) -> None:
    study_entity = ro_crate_metadata.get_object("./")

    default_dataset_ref = entity_ref(DEFAULT_DATASET_TITLE)
    existing_refs = list(study_entity.hasPart)
    if any(existing_ref.id == default_dataset_ref.id for existing_ref in existing_refs):
        return

    updated_study = study_entity.model_copy(
        update={"hasPart": existing_refs + [default_dataset_ref]}
    )
    ro_crate_metadata.update_entity(updated_study)


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

    Note: the validator for additional files in the modification config requires at
    least one of data_directories or patterns to be given, so we assume safety here,
    and don't check that the candidate pool has actually been filtered.
    """
    dataset_id = resolve_dataset_id_by_name(ro_crate_metadata, dataset_config.name)
    if dataset_id is None:
        return

    dataset_col_id = get_dataset_column_id(file_list)
    path_col_id = get_path_column_id(file_list)
    if not _require_columns(
        dataset_name=dataset_config.name,
        assignment_name="additional_files assignment",
        columns={"dataset": dataset_col_id, "file_path": path_col_id},
    ):
        return

    unassigned_mask = file_list.data[dataset_col_id].isna()
    candidate_rows = file_list.data[unassigned_mask]

    additional_files = dataset_config.additional_files

    if additional_files.data_directories:
        directory_patterns = [
            f"{directory.rstrip('/')}/**"
            for directory in additional_files.data_directories
        ]
        candidate_rows = candidate_rows[
            candidate_rows[path_col_id].apply(
                lambda path: match_patterns(str(path), directory_patterns)
            )
        ]

    if additional_files.patterns:
        candidate_rows = candidate_rows[
            candidate_rows[path_col_id].apply(
                lambda path: match_patterns(str(path), additional_files.patterns)
            )
        ]

    if candidate_rows.empty:
        logger.warning(
            f"Dataset '{dataset_config.name}': additional_files matched no unassigned files."
        )
        return

    file_list.data.loc[candidate_rows.index, dataset_col_id] = dataset_id

    logger.info(
        f"Dataset '{dataset_config.name}': {len(candidate_rows)} unassigned file(s) "
        "assigned via additional_files."
    )

    if not additional_files.images:
        return

    type_col_id = get_or_add_type_column_id(file_list)

    for img_assignment in additional_files.images:
        matched_rows = candidate_rows[
            candidate_rows[path_col_id].apply(
                lambda path, patterns=img_assignment.patterns: match_patterns(
                    str(path), patterns
                )
            )
        ]
        matched_indices = matched_rows.index

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


def assign_result_data_for_dataset(
    file_list: FileList,
    ro_crate_metadata: BIAROCrateMetadata,
    dataset_config: DatasetModificationConfig,
) -> None:
    """
    Assign result data — images and annotations — to a dataset.

    Also assigns protocols from image_groups. Annotation assignments write
    labels and annotation method metadata here; image label-writing is left to
    downstream specimen track identification.
    """
    if (
        dataset_config.images is None
        and not dataset_config.image_groups
        and not dataset_config.annotations
    ):
        return

    dataset_id = resolve_dataset_id_by_name(ro_crate_metadata, dataset_config.name)
    if dataset_id is None:
        return

    dataset_col_id = get_dataset_column_id(file_list)
    path_col_id = get_path_column_id(file_list)
    if not _require_columns(
        dataset_name=dataset_config.name,
        assignment_name="result data assignment",
        columns={"dataset": dataset_col_id, "file_path": path_col_id},
    ):
        return

    type_col_id = get_or_add_type_column_id(file_list)

    assignment_context = ResultAssignmentContext(
        file_list=file_list,
        dataset_name=dataset_config.name,
        dataset_id=dataset_id,
        dataset_col_id=dataset_col_id,
        path_col_id=path_col_id,
        type_col_id=type_col_id,
    )

    if dataset_config.images:
        assigned_images = _apply_result_assignment(
            assignment_context=assignment_context,
            assignment_name="image assignment",
            patterns=_patterns_from_image_config(dataset_config.images),
            result_type=FILE_TYPE_IMAGE,
        )
        if assigned_images:
            logger.debug(
                f"Dataset '{assignment_context.dataset_name}': {assigned_images} file(s) "
                f"assigned as {FILE_TYPE_IMAGE}."
            )
        logger.info(
            f"Dataset '{assignment_context.dataset_name}': {assigned_images} file(s) "
            "assigned as image(s)."
        )

    if dataset_config.image_groups:
        _assign_image_group_protocols(assignment_context, dataset_config.image_groups)

    if dataset_config.annotations:
        label_col_id = get_or_add_label_column_id(file_list)
        annotation_method_col_id = get_or_add_associated_annotation_method_column_id(
            file_list
        )
        source_image_col_id = get_or_add_associated_source_image_column_id(file_list)
        _ensure_object_columns(
            file_list,
            [label_col_id, annotation_method_col_id, source_image_col_id],
        )

        assigned_annotations = 0
        for annotation_config in dataset_config.annotations:
            annotation_method_values = [
                title_to_id(title)
                for title in annotation_config.annotation_method_titles
            ]
            extra_column_values = {
                annotation_method_col_id: file_list_association_value(
                    annotation_method_values
                ),
                source_image_col_id: file_list_association_value(
                    annotation_config.associated_source_image
                ),
            }

            assigned_annotations += _apply_result_assignment(
                assignment_context=assignment_context,
                assignment_name="annotation assignment",
                patterns=annotation_config.patterns,
                result_type=FILE_TYPE_ANNOTATION,
                label_col_id=label_col_id,
                label_builder=lambda file_path, config=annotation_config: (
                    _build_annotation_label(config, file_path)
                ),
                extra_column_values=extra_column_values,
            )

        _update_dataset_annotation_methods(
            ro_crate_metadata,
            dataset_id,
            dataset_config.annotations,
        )
        logger.info(
            f"Dataset '{assignment_context.dataset_name}': {assigned_annotations} file(s) "
            "assigned as annotation data."
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
    if not _require_columns(
        dataset_name=DEFAULT_DATASET_TITLE,
        assignment_name="unassigned_files assignment",
        columns={"dataset": dataset_col_id},
    ):
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
            **{
                "@id": default_dataset_id,
                "@type": ["Dataset", type_for(ro_crate_models.Dataset)],
                "name": DEFAULT_DATASET_TITLE,
            }
        )
        ro_crate_metadata.add_entity(default_dataset)
        logger.info(f"Created default dataset entity: {default_dataset_id}")

    _add_default_dataset_to_study_has_part(ro_crate_metadata)

    file_list.data.loc[unassigned_mask, dataset_col_id] = default_dataset_id
    logger.info(
        f"Default dataset: {unassigned_count} unassigned file(s) assigned to "
        f"'{DEFAULT_DATASET_TITLE}'."
    )
