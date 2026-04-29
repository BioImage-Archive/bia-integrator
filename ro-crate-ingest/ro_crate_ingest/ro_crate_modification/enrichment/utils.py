import glob
import logging
import re
from pathlib import Path
from urllib.parse import quote

from bia_ro_crate.models import ro_crate_models
from bia_ro_crate.models.linked_data.ontology_terms import BIA
from bia_ro_crate.models.linked_data.pydantic_ld.LDModel import ObjectReference
from bia_ro_crate.core.bia_ro_crate_metadata import BIAROCrateMetadata

logger = logging.getLogger(__name__)

FILE_TYPE_IMAGE = str(BIA.Image)
FILE_TYPE_ANNOTATION = str(BIA.AnnotationData)


def title_to_id(title: str) -> str:
    return f"#{quote(title)}"


def entity_ref(title: str) -> ObjectReference:
    """Build an ObjectReference pointing to the entity with this title-derived @id."""
    return ObjectReference(**{"@id": title_to_id(title)})


def entity_refs(titles: list[str]) -> list[ObjectReference]:
    """Build ObjectReferences pointing to entities with these title-derived @ids."""
    return [entity_ref(title) for title in titles]


def file_list_association_value(values: list[str]) -> str | None:
    """
    Format values for multivalued file-list association columns.

    The TSV parser expands these columns back to lists on read. 
    Single values are written as plain scalars and multiple values are written
    as a stringified list.
    """
    if not values:
        return None
    return str(values) if len(values) > 1 else values[0]


def type_for(model_cls) -> str:
    full_uri = str(model_cls.model_config["model_type"])
    bia_prefix = str(BIA)
    if full_uri.startswith(bia_prefix):
        return "bia:" + full_uri[len(bia_prefix) :]
    return full_uri


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
