import logging

from bia_ro_crate.models import ro_crate_models
from bia_ro_crate.core.bia_ro_crate_metadata import BIAROCrateMetadata
from bia_ro_crate.models.linked_data.pydantic_ld.LDModel import ObjectReference
from ro_crate_ingest.empiar_to_ro_crate.entity_conversion.publication import (
    get_publication,
)
from ro_crate_ingest.ro_crate_modification.modification_config import StudyMetadata

logger = logging.getLogger(__name__)


def _ref_id(value) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return value.get("@id")
    return getattr(value, "id", None) or getattr(value, "@id", None)


def _merge_publication_refs(
    existing_values,
    publication_ids: list[str],
) -> list[ObjectReference]:
    merged_ids: list[str] = []
    for value in list(existing_values) + publication_ids:
        ref_id = _ref_id(value)
        if ref_id and ref_id not in merged_ids:
            merged_ids.append(ref_id)
    return [ObjectReference(**{"@id": ref_id}) for ref_id in merged_ids]


def add_study_metadata(
    ro_crate_metadata: BIAROCrateMetadata,
    study_metadata: StudyMetadata,
) -> None:
    """
    Add information to study entity, based on provided config.
     - description -> description
     - see_also -> seeAlso
     - related_publication -> relatedPublication
    """
    study_entity = ro_crate_metadata.get_object("./")
    if not isinstance(study_entity, ro_crate_models.Study):
        raise ValueError("Study entity not found in ro-crate.")

    publication_ids: list[str] = []
    for publication_doi in study_metadata.related_publication:
        publication_entity = get_publication(publication_doi)
        if ro_crate_metadata.get_object(publication_entity.id) is None:
            ro_crate_metadata.add_entity(publication_entity)
            logger.debug(f"Added Publication: {publication_entity.id}")
        publication_ids.append(publication_entity.id)
    
    # TODO: should description be additive or overwrite?
    updated = study_entity.model_copy(update={
        "description": study_metadata.description if study_metadata.description is not None else study_entity.description,
        "seeAlso": list(study_entity.seeAlso) + list(study_metadata.see_also), 
        "relatedPublication": _merge_publication_refs(
            study_entity.relatedPublication,
            publication_ids,
        ),
    })

    ro_crate_metadata.update_entity(updated)
    logger.debug(f"Applied metadata additions to study object '{study_entity.name}'.")
