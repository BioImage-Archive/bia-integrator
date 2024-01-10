import logging
from bia_integrator_api import models as api_models
from bia_integrator_core import models as core_models
from bia_integrator_core.image import get_images
from bia_integrator_core.fileref import get_filerefs
from bia_integrator_core.annotation import get_study_annotations, get_image_annotations, get_study_tags
from bia_integrator_core.representation import get_representations
from bia_integrator_core.study import get_study
from bia_integrator_core.config import settings

logger = logging.getLogger(__name__)

def load_and_annotate_study(accession_id: str) -> core_models.BIAStudy:
    """Load the study, merge annotations, and return the result."""

    # annotations always applied, since this is backward-compatible, and resulting object is never written back anyway
    api_study = get_study(accession_id, apply_annotations=True)
    study_images = get_images(accession_id, apply_annotations=True)
    study_filerefs = get_filerefs(accession_id, apply_annotations=True)

    # images dict indexed by image_id (uuid?)
    # annotations dict indexed by annotation_key (refactor if used, but to what? Annotations are lists in the image object, don't have accession/uuid)
    # TODO: Handle downstream changes
    #   what should be the image/annotation id?

    core_study = core_models.BIAStudy(
        # DocumentMixin
        uuid = api_study.uuid,
        version = api_study.version,
        model = api_study.model,

        # BIAStudy
        title = api_study.title,
        description = api_study.description,
        authors = api_study.authors,
        organism = api_study.organism,
        release_date = api_study.release_date,
        accession_id = api_study.accession_id,
        imaging_type = api_study.imaging_type,
        attributes = api_study.attributes,
        annotations = api_study.annotations,
        example_image_uri = api_study.example_image_uri,
        example_image_annotation_uri = api_study.example_image_annotation_uri,
        tags = api_study.tags,
        file_references_count = api_study.file_references_count,
        images_count = api_study.images_count,

        # extra
        images = study_images,
        file_references = study_filerefs,
        annotations_applied=api_study.annotations_applied
    )

    return core_study
