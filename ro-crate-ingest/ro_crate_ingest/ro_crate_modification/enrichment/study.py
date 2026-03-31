import logging

from bia_shared_datamodels import ro_crate_models
from ro_crate_ingest.bia_ro_crate.bia_ro_crate_metadata import BIAROCrateMetadata
from ro_crate_ingest.ro_crate_modification.modification_config import StudyMetadata

logger = logging.getLogger(__name__)


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
    
    # TODO: should description be additive or overwrite?
    updated = study_entity.model_copy(update={
        "description": study_metadata.description if study_metadata.description is not None else study_entity.description,
        "seeAlso": list(study_entity.seeAlso) + list(study_metadata.see_also), 
        "relatedPublication": list(study_entity.relatedPublication) + list(study_metadata.related_publication),
    })

    ro_crate_metadata.update_entity(updated)
    logger.debug(f"Applied metadata additions to study object '{study_entity.name}'.")
