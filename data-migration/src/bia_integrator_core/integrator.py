import logging
from .models import BIAImage, BIAStudy
from .image import get_images
from .annotation import get_study_annotations, get_image_annotations, get_study_tags
from .representation import get_representations
from .study import get_study

logger = logging.getLogger(__name__)

def load_and_annotate_study(accession_id: str) -> BIAStudy:
    """Load the study, merge annotations, and return the result."""

    study = get_study(accession_id)

    study_annotations = get_study_annotations(accession_id)
    study_field_names = [f.name for f in BIAStudy.__fields__.values()]
    for annotation in study_annotations:
        if annotation.key in study_field_names:
            study.__dict__[annotation.key] = annotation.value
        else:
            study.attributes[annotation.key] = annotation.value

    additional_images = get_images(accession_id)
    study.images.update(additional_images)


    # TODO - refactor the image annotation into a separate function
    image_field_names = [f.name for f in BIAImage.__fields__.values()]
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
    

    return study
