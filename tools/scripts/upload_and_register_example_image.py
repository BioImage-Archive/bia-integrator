import logging
import click

from bia_integrator_tools.io import copy_local_to_s3
from bia_integrator_core.models import StudyAnnotation
from bia_integrator_core.interface import persist_study_annotation


logger = logging.getLogger(__file__)


@click.command()
@click.argument('input_image_fpath')
@click.argument('accession_id')
def main(input_image_fpath, accession_id):

    logging.basicConfig(level=logging.INFO)

    dst_key = f"{accession_id}-example.png"
    example_image_uri = copy_local_to_s3(input_image_fpath, dst_key)

    logger.info(f"Uploaded as {example_image_uri}")

    annotation = StudyAnnotation(
        accession_id=accession_id,
        key="example_image_uri",
        value=example_image_uri
    )
    persist_study_annotation(annotation)

        
if __name__ == "__main__":
    main()