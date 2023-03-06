import click
import logging

from bia_integrator_core.models import BIAImageAlias
from bia_integrator_core.config import settings
from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.interface import (
    get_image_annotations,
    persist_image_annotation,
    get_representations,
    persist_image_representation,
    persist_image_alias
)

from bia_integrator_tools.biostudies import load_submission

from assign_single_image_from_fileref import create_and_persist_image_from_fileref
from ingest_from_biostudies import filerefs_from_bst_submission


logger = logging.getLogger(__file__)


@click.command()
@click.argument('accession_id')
def main(accession_id):

    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)
    bst_submission = load_submission(accession_id)
    filerefs = filerefs_from_bst_submission(bst_submission)

    ref_mapping = {fr.uri: fr for fr in filerefs}

    identifier_to_fileref_mapping = {}
    for image_id, image in bia_study.images.items():
        for rep in image.representations:
            if rep.type == "fire_object":
                identifier_to_fileref_mapping[image_id] = ref_mapping[rep.uri]

    for old_image_id, fileref in identifier_to_fileref_mapping.items():
        new_image_id = create_and_persist_image_from_fileref(accession_id, fileref)

        for rep in get_representations(accession_id, old_image_id):
            rep.image_id = new_image_id
            persist_image_representation(rep)

        for ann in get_image_annotations(accession_id, old_image_id):
            ann.image_id = new_image_id
            persist_image_annotation(ann)

        if old_image_id.startswith("IM"):
            alias = BIAImageAlias(
                accession_id=accession_id,
                name=old_image_id,
                image_id=new_image_id
            )
            persist_image_alias(alias)


if __name__ == "__main__":
    main()