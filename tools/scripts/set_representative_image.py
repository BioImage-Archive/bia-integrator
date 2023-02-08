import logging
import click

from bia_integrator_core.models import StudyAnnotation
from bia_integrator_core.interface import persist_study_annotation
from bia_integrator_core.integrator import load_and_annotate_study


logger = logging.getLogger(__file__)


def get_representations_dict(accession_id, image_id):
    bia_study = load_and_annotate_study(accession_id)
    representations = bia_study.images[image_id].representations

    return {rep.type: rep for rep in representations}


def get_representation_by_type(accession_id, image_id, type):

    representations_dict = get_representations_dict(accession_id, image_id)

    return representations_dict[type]


@click.command()
@click.argument('accession_id')
@click.argument('image_id')
def main(accession_id, image_id):

    logging.basicConfig(level=logging.INFO)
    representative_image = get_representation_by_type(accession_id, image_id, "representative")

    annotation = StudyAnnotation(
        accession_id=accession_id,
        key="example_image_uri",
        value=representative_image.uri
    )
    persist_study_annotation(annotation)

        
if __name__ == "__main__":
    main()