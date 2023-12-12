import logging

import click
from bia_integrator_core.interface import load_and_annotate_study
from bia_integrator_core.interface import settings
from bia_integrator_core.interface import api_models

import re
from urllib.request import urlopen
import tempfile

@click.command()
@click.argument('accession_id')
def main(accession_id):

    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)

    for image in bia_study.images:
        if not image.representations:
            continue
        
        # default to empty list instead of null?
        image.annotations = image.annotations if image.annotations else []

        image_ome_ngff = [img_repr for img_repr in image.representations if img_repr.type == "ome_ngff"]
        if len(image_ome_ngff) == 0:
            # no ngff representation
            continue
        elif len(image_ome_ngff) == 1:
            image_ome_ngff = image_ome_ngff.pop()
        else:
            # @TODO: Can we have this case? Adding to make it obvious when we do and decide then
            raise Exception(f"Image {image.uuid} has {len(image_ome_ngff)} ome_ngff representations. Which one to choose?")

        # Odd regex to at least make it invariant to url path, as long as it has a directory with .zarr somewhere
        #   e.g. sometimes urls end in myzarr.zarr, other times in myzarr.zarr/0
        # @TODO: Make this more robust? 
        ome_ngff_uri = re.sub(
            r"\.zarr.*",
            ".zarr/OME/METADATA.ome.xml",
            image_ome_ngff.uri[0]
        )
        logging.info(f"Setting {ome_ngff_uri} as the ome xml of image {image.uuid}")

        ome_metadata_contents = urlopen(ome_ngff_uri).read()
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(ome_metadata_contents)
            # THIS IS MEGA-IMPORTANT!
            #   If the ome xml is small, it doesn't get flushed to disk
            #   but openapi-client independently opens the file passed by path and reads it when posting
            #   so it will post a file with 0 length
            tmp.flush()


            settings.api_client.set_image_ome_metadata(image_uuid=image.uuid, ome_metadata_file = tmp.name)
            
        image.version += 1
        settings.api_client.update_image(image)
        logging.info(f"Updated image {image.uuid}")

if __name__ == "__main__":
    main()
