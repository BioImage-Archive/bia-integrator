import logging
from openapi_client import models as api_models
from bia_integrator_core import models as core_models
from bia_integrator_core.image import get_images
from bia_integrator_core.fileref import get_filerefs
from bia_integrator_core.annotation import get_study_annotations, get_image_annotations, get_study_tags
from bia_integrator_core.representation import get_representations
from bia_integrator_core.study import get_study

logger = logging.getLogger(__name__)

def load_and_annotate_study(accession_id: str) -> core_models.BIAStudy:
    """Load the study, merge annotations, and return the result."""

    api_study = get_study(accession_id)
    study_images = get_images(accession_id)
    study_filerefs = get_filerefs(accession_id)

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
        filerefs = study_filerefs
    )

    """
    Commented for reference - code above might not be correct
    core issue is cascading model decisions when moving to api (e.g. images can't be under study, )
    

    study_annotations = get_study_annotations(accession_id)
    study_field_names = [f.name for f in api_models.BIAStudy.__fields__.values()]
    for annotation in study_annotations:
        if annotation.key in study_field_names:
            study.__dict__[annotation.key] = annotation.value
        else:
            study.attributes[annotation.key] = annotation.value

    additional_images = get_images(accession_id)
    study.images.update(additional_images)

    # TODO - refactor the image annotation into a separate function
    image_field_names = [f.name for f in api_models.BIAImage.__fields__.values()]
    for image_id, image in study.images.items():
        image_annotations = get_image_annotations(accession_id, image_id)
        for image_annotation in image_annotations:
            # We do not want to override the image 'id'
            if image_annotation.key == "id":
                logger.warn(f"Not overriding image.id for {accession_id}:{image_id} with annotation {{ '{image_annotation.key}': '{image_annotation.value}' }}")
                continue
            if image_annotation.key in image_field_names:
                study.images[image_id].__dict__[image_annotation.key] = image_annotation.value
            else:
                study.images[image_id].attributes[image_annotation.key] = image_annotation.value
        additional_image_reps = get_representations(accession_id, image_id)
        image.representations += additional_image_reps

    tag_annotations = get_study_tags(accession_id)
    study.tags |= tag_annotations
    """    

    return core_study
