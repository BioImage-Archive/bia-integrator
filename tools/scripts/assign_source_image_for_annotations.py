"""Adds source_image as annotation to file references in a study where applicable."""
import click
import logging

from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.interface import update_fileref

logger = logging.getLogger(__file__)

@click.command()
@click.argument('accession_id')
@click.option("--fname_separator", default="_seg", show_default=True, help="Source file vs annotation file name separator")

def main(accession_id,fname_separator):
    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)

    fname_dict = {'S-BIAD633':'xml', 'S-BIAD599':'_seg','S-BIAD463':'_rgb_labels',
                  'S-BIAD531':'ome_','S-BIAD843':'_segmented','S-BIAD900':'_mask'}
    if fname_separator == '_seg' and accession_id in fname_dict.keys():
        fname_separator = fname_dict[accession_id]

    # workaround for S-BIAD531
    if fname_separator == 'ome_':
        image_names = {str(image.name).split('/')[-1]: image.name for image in bia_study.images}
        for fileref in bia_study.file_references:
            name = str(fileref.name)
            source_image = None
            if fname_separator == 'ome_' and fname_separator in name:           
                name = name.split('/')[-1]
                source_image_name = name.split('ome_')[0] + 'ome.tif'
                if source_image_name in image_names.keys():
                    source_image = image_names[source_image_name]
            if source_image:
                    fileref.attributes['source image'] = source_image
    
    for fileref in bia_study.file_references:
        if not fileref.attributes.get('source image'):
            source_image = None
            name = str(fileref.name)
            if fname_separator in ['_seg','_segmented'] and fname_separator in name :
                source_image = name.replace(fname_separator,'')
            elif fname_separator == 'ome_' and fname_separator in name :
                name = name.split('/')[-1]
                source_image_name = name.split('ome_')[0] + 'ome.tif'
                if source_image_name in image_names.keys():
                    source_image = image_names[source_image_name]
            elif fname_separator == '_rgb_labels': 
                if fname_separator in name:
                    source_image = name.replace('_rgb_labels','')
                elif 'annotation' in name:
                    source_image = name
            elif fname_separator == 'xml' and fname_separator in name:
                source_image = name.replace('xml','tif')
            elif fname_separator == '_mask' and fname_separator in name :
                source_image = name.split('_mask.png')[0] + '.tif'
            if source_image:
                fileref.attributes['source image'] = source_image
                update_fileref(fileref)


if __name__ == "__main__":
    main()
