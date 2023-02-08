import logging
import click

from bia_integrator_core.models import BIAImageRepresentation
from bia_integrator_core.interface import persist_image_representation


logger = logging.getLogger(__file__)


@click.command()
@click.argument('accession_id')
@click.argument('image_id')
@click.argument('uri')
def main(accession_id, image_id, uri):

    logging.basicConfig(level=logging.INFO)

    rep = BIAImageRepresentation(
        accession_id=accession_id,
        image_id=image_id,
        uri=uri,
        size=0,
        type="ome_ngff",
        dimensions=None,
        attributes={},
        rendering=None
    )

    persist_image_representation(rep)

        
if __name__ == "__main__":
    main()