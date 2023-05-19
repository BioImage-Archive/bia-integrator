import click
import logging

from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_tools.cli import create_image_annotation

logger = logging.getLogger(__file__)

@click.command()
@click.argument('accession_id')
@click.option("-fs","--fname_separator", default="_seg", show_default=True, help="Source file vs annotation file name separator")

def main(accession_id,fname_separator):
    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)
    for image_id, image in bia_study.images.items():
        if not image.attributes.get('source_image'):
            if fname_separator == '_seg':
                source_image = str(image.original_relpath).replace('_seg','')
            elif fname_separator == 'ome_':
                source_image = str(image.original_relpath).split('ome_')[0] + 'ome.tif'
            create_image_annotation(accession_id,image_id,'source_image',source_image)


if __name__ == "__main__":
    main()