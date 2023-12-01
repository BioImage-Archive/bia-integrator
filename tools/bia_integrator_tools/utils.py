import uuid
import logging
import hashlib
import pathlib
from typing import Optional
import requests

from ome_zarr.io import parse_url
from ome_zarr.reader import Reader
from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_api.models import BIAImageRepresentation, BIAImage
from bia_integrator_api.models import RenderingInfo, ChannelRendering
from bia_integrator_core.interface import persist_image_representation, persist_image, get_image

logger = logging.getLogger(__name__)

def get_annotation_files_by_accession(accession_id):
    """Generate list of files in study that are annotations of another image."""
    
    bia_study = load_and_annotate_study(accession_id)
    return [
        fileref for fileref in bia_study.file_references
        if "source image" in fileref.attributes
    ]

def get_annotation_images_in_study(accession_id):
    """Generate a dictionary of images in study that are annotations of another image."""

    bia_study = load_and_annotate_study(accession_id)
    annot_fileref_names = [
        fileref.name for fileref in bia_study.file_references.values()
        if "source image" in fileref.attributes
    ]
    
    return {
        image.id: image for image in bia_study.images.values()
        if image.name in annot_fileref_names 
    }

def get_annotation_image_name_and_source_image_name(accession_id):
    """Generate a dictionary of name and source image name of annotations images in a study."""

    bia_study = load_and_annotate_study(accession_id)
    return {
        fileref.name: fileref.attributes['source image'] for fileref in bia_study.file_references.values()
        if "source image" in fileref.attributes
    }
    

def get_source_images_in_study(accession_id):
    """Generate a dictionary of images in study that are source images of an annotation file."""

    bia_study = load_and_annotate_study(accession_id)
    annot_and_image = get_annotation_image_name_and_source_image_name(accession_id)

    return {
        image.id: image 
        for image in bia_study.images.values() 
        if image.name in annot_and_image.values()
    }


def get_image_rep_by_type(image_uuid, rep_type):

    image = get_image(image_uuid)
    for image_rep in image.representations:
        if image_rep.type == rep_type:
            return image_rep

    return None


def get_ome_ngff_rep(image):
    for rep in image.representations:
        if rep.type == "ome_ngff":
            return rep


def get_example_image_uri(accession_id):
    bia_study = load_and_annotate_study(accession_id)
    return bia_study.example_image_uri

def get_example_annotation_uri(accession_id):
    bia_study = load_and_annotate_study(accession_id)
    return bia_study.example_annotation_uri

def get_ome_ngff_rep_by_accession_and_image(accession_id: str, image_id: str) -> Optional[BIAImageRepresentation]:
    image = get_image(image_id)
    
    ome_ngff_rep = get_ome_ngff_rep(image)
    
    return ome_ngff_rep


def set_rendering_info_for_ome_ngff_rep(ome_ngff_rep):
    if not ome_ngff_rep.rendering:
        logger.info(f"No rendering info set, using Zarr OMERO metadata")

        reader = Reader(parse_url(ome_ngff_rep.uri))
        # nodes may include images, labels etc
        nodes = list(reader())
        # first node will be the image pixel data
        image_node = nodes[0]

        chrenders = [
            ChannelRendering(
                colormap_start=colormap_start,
                colormap_end=colormap_end
            )
            for colormap_start, colormap_end in image_node.metadata['colormap']
        ]

        ome_ngff_rep.rendering = RenderingInfo(
            channel_renders=chrenders,
            default_z=None,
            default_t=None
        )
        
        persist_image_representation(ome_ngff_rep)


def create_and_persist_image_from_fileref(study_uuid, fileref, rep_type="fire_object", extra_attributes={}):
    """Create a new image, together with a single representation from one file
    reference."""

    name = fileref.name
    logger.info(f"Assigned name {name}")

    hash_input = fileref.uuid
    hexdigest = hashlib.md5(hash_input.encode("utf-8")).hexdigest()
    image_id_as_uuid = uuid.UUID(version=4, hex=hexdigest)
    image_id = str(image_id_as_uuid)

    image_rep = BIAImageRepresentation(
        image_id=image_id,
        size=fileref.size_in_bytes,
        uri=[fileref.uri,],
        attributes={"fileref_ids": [fileref.uuid]},
        type=rep_type
    )
    if extra_attributes:
        for key, value in extra_attributes.items():
            image_rep.attributes["key"] = value

    image = BIAImage(
        uuid=image_id,
        version=0,
        study_uuid=study_uuid,
        original_relpath=name,
        name=name,
        representations=[image_rep],
        attributes=fileref.attributes
    )

    persist_image(image)

    return image_id

def url_exists(url: str) -> bool:
    
    try:
        response = requests.head(url)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def list_of_objects_to_dict(object_list: list, key: str = "uuid") -> dict:
    """Convert list of objs to dict with keys from specifed obj property"""

    return { obj.__dict__[key]: obj for obj in object_list }
