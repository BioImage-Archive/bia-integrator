"""Copy a local OME-Zarr file to S3 storage. The S3 path will be determined
automatically, using the image's accession identifier and image identifier.
"""

import logging

import click

from bia_integrator_tools.io import upload_dirpath_as_zarr_image_rep


logging.getLogger(__file__)


@click.command()
@click.argument("zarr_fpath")
@click.argument("accession_id")
@click.argument("image_id")
def main(zarr_fpath, accession_id, image_id):

    logging.basicConfig(level=logging.INFO)

    zarr_uri = upload_dirpath_as_zarr_image_rep(zarr_fpath, accession_id, image_id)

    print(f"Uploaded, URI: {zarr_uri}")


if __name__ == "__main__":
    main()