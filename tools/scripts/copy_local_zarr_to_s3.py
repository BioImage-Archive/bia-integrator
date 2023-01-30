import logging
from pathlib import Path

import click

from bia_integrator_tools.io import copy_local_zarr_to_s3


logging.getLogger(__file__)


@click.command()
@click.argument("zarr_fpath")
@click.argument("accession_id")
@click.argument("image_id")
def main(zarr_fpath, accession_id, image_id):

    logging.basicConfig(level=logging.INFO)

    zarr_uri = copy_local_zarr_to_s3(Path(zarr_fpath), accession_id, image_id)

    print(zarr_uri)


if __name__ == "__main__":
    main()