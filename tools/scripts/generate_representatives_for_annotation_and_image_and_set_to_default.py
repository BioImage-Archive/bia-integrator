import logging
import tempfile

import click
from bia_integrator_core.models import BIAImageRepresentation, StudyAnnotation, RenderingInfo, ChannelRendering
from bia_integrator_core.interface import persist_image_representation, persist_study_annotation
from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_tools.utils import (
    get_ome_ngff_rep_by_accession_and_image,
    get_annotation_files_by_accession,
    get_annotation_images_in_study,
    get_source_images_in_study,
    get_annotation_image_name_and_source_image_name,
    get_example_image_uri, get_example_annotation_uri
)
from bia_integrator_tools.io import copy_local_to_s3
from bia_integrator_tools.rendering import (
    NGFFProxyImage, render_proxy_image, generate_padded_thumbnail_from_ngff_uri
)

logger = logging.getLogger(__file__)

def generate_annotation_representative(accession_id: str, image_id: str):
    """Generate representative annotation image from source image id and persist it"""

    logging.info(f"Attempting to create representative annotation for %s %s" %(accession_id, image_id))
    # Check if there's already a representative annotation. If so do not overwrite.
    if get_example_annotation_uri(accession_id):
        logging.info(f"There is a representative annotation already. Terminating the script")
        return
    
    ome_ngff_rep = get_ome_ngff_rep_by_accession_and_image(accession_id, image_id)
    w = 512
    h = 512
    im = generate_padded_thumbnail_from_ngff_uri(ome_ngff_rep.uri, dims=(w,h))
    dst_key = f"{accession_id}/{accession_id}-annotation-representative-{w}-{h}.png"

    with tempfile.NamedTemporaryFile(suffix=".png") as fh:
        im.save(fh)
        uri = copy_local_to_s3(fh.name, dst_key)
        logger.info(f"Wrote representative image to {uri}")

    rep = BIAImageRepresentation(
        accession_id=accession_id,
        image_id=image_id,
        size=0,
        uri=uri,
        type="representative",
        dimensions=str((w, h)),
        attributes=None,
        rendering=None
    )

    persist_image_representation(rep)

    annotation = StudyAnnotation(
        accession_id=accession_id,
        key="example_annotation_uri",
        value=uri
    )
    persist_study_annotation(annotation)

def generate_image_representative(accession_id: str, image_id: str):
    """Generate representative image from image id and persist it"""

    logging.info(f"Attempting to create representative image for %s %s" %(accession_id, image_id))
    # Check if there's already a representative image. If so do not overwrite.
    if get_example_image_uri(accession_id):
        logging.info(f"There is a representative image already. Terminating the script")
        return
    
    ome_ngff_rep = get_ome_ngff_rep_by_accession_and_image(accession_id, image_id)
    w = 512
    h = 512
    im = generate_padded_thumbnail_from_ngff_uri(ome_ngff_rep.uri, dims=(w,h))
    dst_key = f"{accession_id}/{accession_id}-representative-{w}-{h}.png"

    with tempfile.NamedTemporaryFile(suffix=".png") as fh:
        im.save(fh)
        uri = copy_local_to_s3(fh.name, dst_key)
        logger.info(f"Wrote representative image to {uri}")

    rep = BIAImageRepresentation(
        accession_id=accession_id,
        image_id=image_id,
        size=0,
        uri=uri,
        type="representative",
        dimensions=str((w, h)),
        attributes=None,
        rendering=None
    )

    persist_image_representation(rep)

    annotation = StudyAnnotation(
        accession_id=accession_id,
        key="example_image_uri",
        value=uri
    )
    persist_study_annotation(annotation)

@click.command()
@click.argument('accession_id')
@click.argument('image_id')
def main(accession_id, image_id):

    logging.basicConfig(level=logging.INFO)
      
    annot_files = get_annotation_files_by_accession(accession_id)
    if annot_files:
        logging.info(f"This dataset has annotation images")
        annot_images = get_annotation_images_in_study(accession_id)
        source_images = get_source_images_in_study(accession_id)
        annot_assoc = get_annotation_image_name_and_source_image_name(accession_id)
        if image_id in annot_images.keys():
            generate_annotation_representative(accession_id, image_id)
            source_name = annot_assoc[annot_images[image_id].name]
            for image in source_images.values(): 
                if source_name == image.name:
                    generate_image_representative(accession_id,image.id)
        else:
            generate_image_representative(accession_id,image_id)
            source_image = source_images[image_id]
            for key, value in annot_assoc.items():
                if source_image.name == value:
                    annot_name = key
            for annot_image in annot_images.values():
                if annot_image.name == annot_name:
                    generate_annotation_representative(accession_id,annot_image.id)
    else:
        generate_image_representative(accession_id,image_id)



if __name__ == "__main__":
    main()
