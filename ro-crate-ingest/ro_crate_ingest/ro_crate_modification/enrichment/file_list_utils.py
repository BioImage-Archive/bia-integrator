import logging
import re

import pandas as pd
from rdflib import RDF

from bia_ro_crate.core.file_list import FileList
from bia_ro_crate.models import ro_crate_models
from bia_ro_crate.models.linked_data.ontology_terms import BIA, SCHEMA

logger = logging.getLogger(__name__)


IS_PART_OF_PROPERTY = str(SCHEMA.isPartOf)
FILE_PATH_PROPERTY = str(BIA.filePath)
NAME_PROPERTY = str(SCHEMA.name)
RDF_TYPE_PROPERTY = str(RDF.type)
ASSOCIATED_SOURCE_IMAGE_PROPERTY = str(BIA.associatedSourceImage)
LEGACY_SOURCE_IMAGE_LABEL_PROPERTY = "http://bia/sourceImageLabel"
ASSOCIATED_ANNOTATION_METHOD_PROPERTY = str(BIA.associatedAnnotationMethod)
ASSOCIATED_PROTOCOL_PROPERTY = str(BIA.associatedProtocol)
ASSOCIATED_SUBJECT_PROPERTY = str(BIA.associatedSubject)
COLUMN_ID_PATTERN = re.compile(r"^_:col(\d+)$")


def get_dataset_column_id(file_list: FileList) -> str | None:
    """Return the dataset column."""
    return file_list.get_column_id_by_property(IS_PART_OF_PROPERTY)


def get_path_column_id(file_list: FileList) -> str | None:
    """Return the file-path column."""
    return file_list.get_column_id_by_property(FILE_PATH_PROPERTY)


def _next_column_id(file_list: FileList) -> str:
    existing_ids = set(file_list.schema) | set(file_list.data.columns)
    numeric_ids = [
        int(match.group(1))
        for col_id in existing_ids
        if (match := COLUMN_ID_PATTERN.match(col_id))
    ]
    next_index = max(numeric_ids, default=len(file_list.schema) - 1) + 1
    while f"_:col{next_index}" in existing_ids:
        next_index += 1
    return f"_:col{next_index}"


def _ensure_object_column(file_list: FileList, col_id: str) -> None:
    if file_list.data[col_id].dtype != object:
        file_list.data[col_id] = file_list.data[col_id].astype(object)


def _has_value(value) -> bool:
    if isinstance(value, list):
        return bool(value)
    return pd.notna(value)


def _get_or_add_column_id(
    file_list: FileList,
    *,
    property_url: str,
    column_name: str,
    log_level: str = "debug",
) -> str:
    col_id = file_list.get_column_id_by_property(property_url)
    if col_id is not None:
        _ensure_object_column(file_list, col_id)
        return col_id

    column_id = _next_column_id(file_list)
    new_col = ro_crate_models.Column(
        **{
            "@id": column_id,
            "@type": ["csvw:Column"],
            "columnName": column_name,
            "propertyUrl": property_url,
        }
    )
    file_list.add_column(new_col, pd.Series([None] * len(file_list.data)))
    getattr(logger, log_level)(f"Added '{column_name}' column to file list.")
    return new_col.id


def get_or_add_type_column_id(file_list: FileList) -> str:
    return _get_or_add_column_id(
        file_list,
        property_url=RDF_TYPE_PROPERTY,
        column_name="type",
        log_level="info",
    )


def get_or_add_label_column_id(file_list: FileList) -> str:
    return _get_or_add_column_id(
        file_list,
        property_url=NAME_PROPERTY,
        column_name="label",
        log_level="debug",
    )


def get_or_add_associated_source_image_column_id(file_list: FileList) -> str:
    current_col_id = file_list.get_column_id_by_property(
        ASSOCIATED_SOURCE_IMAGE_PROPERTY
    )
    if current_col_id is not None:
        _ensure_object_column(file_list, current_col_id)
        return current_col_id

    legacy_col_id = file_list.get_column_id_by_property(
        LEGACY_SOURCE_IMAGE_LABEL_PROPERTY
    )
    if legacy_col_id is not None:
        _ensure_object_column(file_list, legacy_col_id)
        return legacy_col_id

    return _get_or_add_column_id(
        file_list,
        property_url=ASSOCIATED_SOURCE_IMAGE_PROPERTY,
        column_name="associated_source_image",
        log_level="debug",
    )


def get_or_add_associated_annotation_method_column_id(file_list: FileList) -> str:
    return _get_or_add_column_id(
        file_list,
        property_url=ASSOCIATED_ANNOTATION_METHOD_PROPERTY,
        column_name="associated_annotation_method",
        log_level="debug",
    )


def get_or_add_associated_protocol_column_id(file_list: FileList) -> str:
    return _get_or_add_column_id(
        file_list,
        property_url=ASSOCIATED_PROTOCOL_PROPERTY,
        column_name="associated_protocol",
        log_level="debug",
    )


def get_or_add_associated_subject_column_id(file_list: FileList) -> str:
    return _get_or_add_column_id(
        file_list,
        property_url=ASSOCIATED_SUBJECT_PROPERTY,
        column_name="associated_subject",
        log_level="debug",
    )


def _merge_column_values(
    file_list: FileList, target_col_id: str, source_col_id: str
) -> None:
    target = file_list.data[target_col_id]
    source = file_list.data[source_col_id]
    has_target_value = target.apply(_has_value)
    file_list.data[target_col_id] = target.where(has_target_value, source)


def _drop_column(ro_crate_metadata, file_list: FileList, col_id: str) -> None:
    if col_id in file_list.data.columns:
        file_list.data.drop(columns=[col_id], inplace=True)
    file_list.schema.pop(col_id, None)
    ro_crate_metadata.get_object_lookup().pop(col_id, None)

    file_list_entity = ro_crate_metadata.get_file_list_entity()
    table_schema = ro_crate_metadata.get_object(file_list_entity.tableSchema.id)
    if table_schema is not None:
        table_schema.column = [
            column_ref for column_ref in table_schema.column if column_ref.id != col_id
        ]


def normalize_legacy_associated_source_image_column(
    ro_crate_metadata,
    file_list: FileList,
) -> None:
    """
    Retarget an existing legacy source_image_label column to the newer
    associated_source_image metadata shape.
    """
    legacy_col_id = file_list.get_column_id_by_property(
        LEGACY_SOURCE_IMAGE_LABEL_PROPERTY
    )
    if legacy_col_id is None:
        return

    current_col_id = file_list.get_column_id_by_property(
        ASSOCIATED_SOURCE_IMAGE_PROPERTY
    )
    if current_col_id is not None:
        _merge_column_values(file_list, current_col_id, legacy_col_id)
        _drop_column(ro_crate_metadata, file_list, legacy_col_id)
        return

    column = ro_crate_metadata.get_object(legacy_col_id)
    if column is None:
        return

    column.columnName = "associated_source_image"
    column.propertyUrl = ASSOCIATED_SOURCE_IMAGE_PROPERTY
