import logging
import pathlib

import click
from bia_integrator_core.models import BIAImageRepresentation
from bia_integrator_core.interface import persist_image_representation


logger = logging.getLogger(__file__)


@click.command()
@click.argument("reps_dirpath")
def main(reps_dirpath):
    logging.basicConfig(level=logging.INFO)

    reps_dirpath = pathlib.Path(reps_dirpath)

    for fpath in reps_dirpath.glob("*.json"):
        rep = BIAImageRepresentation.parse_file(fpath)
        persist_image_representation(rep)
        

if __name__ == "__main__":
    main()