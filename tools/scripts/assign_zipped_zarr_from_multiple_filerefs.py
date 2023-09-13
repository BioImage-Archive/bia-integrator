"""Assign images from zipped ome.zarr split across multiple zipfiles

This first version is written to work for the specific case of S-BIAD882
"""

import uuid
import logging
import hashlib

import click
from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.models import BIAImage, BIAImageRepresentation
from bia_integrator_core.image import persist_image

logger = logging.getLogger(__file__)

# FIXME - library code (bia_integrator_tools/utils.py?
def identifier_from_fileref_ids(fileref_ids):
    hash_input = ''.join(fileref_ids)
    hexdigest = hashlib.md5(hash_input.encode("utf-8")).hexdigest()
    image_id_as_uuid = uuid.UUID(version=4, hex=hexdigest)
    image_id = str(image_id_as_uuid)    

    return image_id

@click.command()
@click.argument("accession_id")
def main(accession_id):
    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)

    study_filerefs = bia_study.file_references
    # Map split files to complete zip. Pattern is *.zarr.zip.001 etc
    n_truncate = 4
    basenames = set([fileref.name[:-n_truncate] for fileref in study_filerefs.values()])
    fileref_map = {basename: [] for basename in list(basenames)}
    for fileref in bia_study.file_references.values():
        basename = fileref.name[:-4]
        fileref_map[basename].append(fileref)

    sort_by_name = lambda file_reference: file_reference.name
    [fileref_list.sort(key=sort_by_name) for fileref_list in fileref_map.values()];

    for name, filerefs in fileref_map.items():
        
        fileref_ids = [fileref.id for fileref in filerefs]
        image_id = identifier_from_fileref_ids(fileref_ids)

        image_rep = BIAImageRepresentation(
            accession_id=accession_id,
            image_id=image_id,
            size=sum(fileref.size_in_bytes for fileref in filerefs),
            uri=[fileref.uri for fileref in filerefs],
            attributes={
                "fileref_ids": fileref_ids,
                "path_in_zarr": "/0"
            },
            # Check type - Structured Fileset? split_zipped_zarr?
            type="zipped_zarr"
        )

        image = BIAImage(
            id=image_id,
            accession_id=accession_id,
            original_relpath=name,
            name=name,
            representations=[image_rep]
        )

        persist_image(image)


if __name__ == "__main__":
    main()
