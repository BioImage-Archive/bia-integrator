import sys
from pathlib import Path
import logging

import click

from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_tools.cli import sizeof_fmt
from bia_integrator_core.interface import persist_image_annotation
from bia_integrator_core.interface import api_models
from bia_integrator_tools.utils import list_of_objects_to_dict
from bia_integrator_core.config import settings

logger = logging.getLogger(__file__)

def get_image_download_size(accession_id: str) -> dict:
    """Return formatted size of download of original image

    Return the formatted size of the download of the original image
    from the BIA. This version assumes there is one image per image
    representation - which is not the case for multichannel images.

    Additionally, if the image is in a zip file, the size of the zip file
    that needs to be downloaded is returned (with a relevant message)

    """
    bia_study = load_and_annotate_study(accession_id)
    
    images = list_of_objects_to_dict(bia_study.images)
    download_sizes = {}

    zip_sizes = {}
    file_references = list_of_objects_to_dict(bia_study.file_references)
    for fileref in file_references.values():
        if fileref.uri.endswith(".zip") and fileref.type != "file_in_zip":
            zip_sizes[fileref.uri] = sizeof_fmt(fileref.size_in_bytes)

    for bia_image in images.values():
        for image_representation in bia_image.representations:
            if image_representation.type in ["zipped_zarr", "fire_object"]:
                # TODO: Revisit this when we start dealing with representations
                # composed of more than one file reference
                fileref_ids = image_representation.attributes["fileref_ids"]
                n_fileref_ids = len(fileref_ids)
                if n_fileref_ids > 1:
                    warning_str = [
                        f"image_representation in {bia_image.accession_id} "
                        f"with ID: {bia_image.uuid} has {n_fileref_ids} file "
                        "references. However, only the first one is being "
                        "used to compute download size"
                    ]
                    logger.warning(warning_str)
                if image_representation.type == "fire_object" and image_representation.uri[0].endswith(".zip"):
                    download_size = f"In {zip_sizes[image_representation.uri[0]]} zip"
                else:
                    download_size = sizeof_fmt(file_references[fileref_ids[0]].size_in_bytes)
                    
            download_sizes[bia_image.uuid] = download_size
                
    return download_sizes

@click.command()
@click.argument("accession_id")
def main(accession_id: str) -> None:
    """Obtain image download sizes and save as annotations for each image

    Obtain the download size of images and save as annotations with 
    appropriate units (KiB, MiB, etc). For images obtained from zip files
    the size is that of the zip file as the zip file has to be downloaded
    to extract the image.
    """
    
    logging.basicConfig(level=logging.INFO)
    
    download_sizes = get_image_download_size(accession_id)
    for image_uuid, download_size in download_sizes.items():
        annotation = api_models.ImageAnnotation(
            # Should we configure env varible for snakemake_pipeline?
            #author_email="snakemake_pipeline@ebi.ac.uk",
            author_email=settings.bia_username,
            key="download_size",
            value=download_size,
            state="active"
        )
        persist_image_annotation(image_uuid, annotation)
    logger.info(download_sizes)

if __name__ == "__main__":
    main()
