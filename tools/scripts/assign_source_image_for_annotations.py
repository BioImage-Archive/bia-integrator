"""Adds source_image as annotation to file references in a study where applicable."""
import click
import logging

from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.interface import persist_study

logger = logging.getLogger(__file__)

@click.command()
@click.argument('accession_id')
@click.option("--fname_separator", default="_seg", show_default=True, help="Source file vs annotation file name separator")

def main(accession_id,fname_separator):
    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)

    fname_dict = {'S-BIAD633':'xml', 'S-BIAD599':'_seg','S-BIAD463':'_rgb_labels',
                  'S-BIAD531':'ome_','S-BIAD843':'_segmented'}
    if fname_separator == '_seg' and accession_id in fname_dict.keys():
        fname_separator = fname_dict[accession_id]

    for fileref in bia_study.file_references.values():
        if not fileref.attributes.get('source image'):
            source_image = None
            name = str(fileref.name)
            if fname_separator == '_seg' and fname_separator in name :
                source_image = name.replace('_seg','')
            elif fname_separator == 'ome_' and fname_separator in name :
                source_image = name.split('ome_')[0] + 'ome.tif'
            elif fname_separator == '_rgb_labels': 
                if fname_separator in name:
                    source_image = name.replace('_rgb_labels','')
                elif 'annotation' in name:
                    source_image = name
            elif fname_separator == 'xml' and fname_separator in name:
                source_image = name.replace('xml','tif')
            if source_image:
                fileref.attributes['source image'] = source_image
    persist_study(bia_study)


if __name__ == "__main__":
    main()