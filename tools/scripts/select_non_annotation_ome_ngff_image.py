"""Select the first non-annotation ome-ngff image of a study."""

import logging

import click
from bia_integrator_tools.utils import (get_non_annotation_images_by_accession,
                                get_ome_ngff_rep_by_accession_and_image
)

logger = logging.getLogger(__file__)


@click.command()
@click.argument('accession_id')

def main(accession_id):
    
    logging.basicConfig(level=logging.INFO)

    images = get_non_annotation_images_by_accession(accession_id)

    for image in images:
        if get_ome_ngff_rep_by_accession_and_image(accession_id,image.id):
            print(image.id)
            return None

#    list_image_ids = [ 
#        image.id for image in images
#        if get_ome_ngff_rep_by_accession_and_image(accession_id,image.id)
#    ]
#    if list_image_ids:
#        return list_image_ids[0]
#    else:


if __name__ == "__main__":
    main()