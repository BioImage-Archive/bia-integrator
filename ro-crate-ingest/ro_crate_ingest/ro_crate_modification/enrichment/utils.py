import glob
import logging
import re
from pathlib import Path
from urllib.parse import quote

import pandas as pd
from rdflib import RDF

from bia_ro_crate.models import ro_crate_models
from bia_ro_crate.models.linked_data.ontology_terms import BIA, SCHEMA
from bia_ro_crate.models.linked_data.pydantic_ld.LDModel import ObjectReference
from bia_ro_crate.core.bia_ro_crate_metadata import BIAROCrateMetadata
from bia_ro_crate.core.file_list import FileList

logger = logging.getLogger(__name__)


RDF_TYPE_PROPERTY = str(RDF.type)
IS_PART_OF_PROPERTY = str(SCHEMA.isPartOf)
FILE_PATH_PROPERTY = str(BIA.filePath)
ASSOCIATED_SOURCE_IMAGE_PROPERTY = str(BIA.associatedSourceImage)
LEGACY_SOURCE_IMAGE_LABEL_PROPERTY = "http://bia/sourceImageLabel"
ASSOCIATED_ANNOTATION_METHOD_PROPERTY = str(BIA.associatedAnnotationMethod)

FILE_TYPE_IMAGE = str(BIA.Image)
FILE_TYPE_ANNOTATION = str(BIA.AnnotationData)


def title_to_id(title: str) -> str:
    return f"#{quote(title)}"


def ref(title: str) -> ObjectReference:
    """Convenience: build an ObjectReference pointing to a title-derived @id."""
    return ObjectReference(**{"@id": title_to_id(title)})


def refs(titles: list[str]) -> list[ObjectReference]:
    """Build a list of ObjectReferences from a list of titles."""
    return [ref(t) for t in titles]


def type_for(model_cls) -> str:
    full_uri = str(model_cls.model_config["model_type"])
    bia_prefix = str(BIA)
    if full_uri.startswith(bia_prefix):
        return "bia:" + full_uri[len(bia_prefix):]
    return full_uri


def _get_or_add_column_id(
    file_list: FileList,
    *,
    property_url: str,
    column_id: str,
    column_name: str,
    coerce_to_object: bool = True,
    log_level: str = "debug",
) -> str:
    col_id = file_list.get_column_id_by_property(property_url)
    if col_id is not None:
        if coerce_to_object and file_list.data[col_id].dtype != object:
            file_list.data[col_id] = file_list.data[col_id].astype(object)
        return col_id

    new_col = ro_crate_models.Column(**{
        "@id": column_id,
        "@type": ["csvw:Column"],
        "columnName": column_name,
        "propertyUrl": property_url,
    })
    file_list.add_column(new_col, pd.Series([None] * len(file_list.data)))
    getattr(logger, log_level)(f"Added '{column_name}' column to file list.")
    return new_col.id


# TODO: which columns are always present? Same for source image, below.
def get_or_add_type_column_id(file_list: FileList) -> str:
    return _get_or_add_column_id(
        file_list,
        property_url=RDF_TYPE_PROPERTY,
        column_id="_:col_type",
        column_name="type",
        coerce_to_object=True,
        log_level="info",
    )


def get_or_add_associated_source_image_column_id(file_list: FileList) -> str:
    legacy_col_id = file_list.get_column_id_by_property(LEGACY_SOURCE_IMAGE_LABEL_PROPERTY)
    if legacy_col_id is not None:
        if file_list.data[legacy_col_id].dtype != object:
            file_list.data[legacy_col_id] = file_list.data[legacy_col_id].astype(object)
        return legacy_col_id

    return _get_or_add_column_id(
        file_list,
        property_url=ASSOCIATED_SOURCE_IMAGE_PROPERTY,
        column_id="_:col_associated_source_image",
        column_name="associated_source_image",
        coerce_to_object=True,
        log_level="debug",
    )


def get_or_add_source_image_label_column_id(file_list: FileList) -> str:
    # Backward-compatible alias: source_image_label now maps to associated_source_image.
    return get_or_add_associated_source_image_column_id(file_list)


def get_or_add_associated_annotation_method_column_id(file_list: FileList) -> str:
    return _get_or_add_column_id(
        file_list,
        property_url=ASSOCIATED_ANNOTATION_METHOD_PROPERTY,
        column_id="_:col_associated_annotation_method",
        column_name="associated_annotation_method",
        coerce_to_object=True,
        log_level="debug",
    )


def get_dataset_column_id(file_list: FileList) -> str | None:
    return file_list.get_column_id_by_property(IS_PART_OF_PROPERTY)


def get_path_column_id(file_list: FileList) -> str | None:
    return file_list.get_column_id_by_property(FILE_PATH_PROPERTY)


def resolve_dataset_id_by_name(
    ro_crate_metadata: BIAROCrateMetadata,
    name: str,
) -> str | None:
    """
    Look up a Dataset entity in the RO-Crate by its name field.
    Returns the entity @id if found, None otherwise.
    """
    datasets = ro_crate_metadata.get_objects_by_type().get(ro_crate_models.Dataset, {})
    for entity_id, entity in datasets.items():
        if getattr(entity, "name", None) == name:
            return entity_id
    logger.warning(f"No dataset with name '{name}' found in RO-Crate metadata.")
    return None


def match_patterns(file_path: str, patterns: list[str]) -> bool:
    """Return True if file_path matches any of the given glob patterns."""
    for pattern in patterns:
        try:
            regex = glob.translate(pattern, recursive=True, include_hidden=True)
            if re.match(regex, file_path):
                return True
        except TypeError:
            if Path(file_path).match(pattern):
                return True
    return False
