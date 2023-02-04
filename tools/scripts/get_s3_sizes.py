import logging
import subprocess
from urllib.parse import urlparse

import click
import pandas as pd

from bia_integrator_core.interface import (
    get_all_study_identifiers,
    persist_image_representation
)
from bia_integrator_core.integrator import (
    load_and_annotate_study
)

from bia_integrator_tools.utils import get_ome_ngff_rep


logger = logging.getLogger(__file__)


def full_s3_uri_to_size_in_bytes(full_s3_uri):

    parsed_url = urlparse(full_s3_uri)
    endpoint_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    s3_prefix = parsed_url.path[1:]

    cmd = f"aws --endpoint-url {endpoint_url} s3 ls --summarize --recursive s3://{s3_prefix}"

    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    try:
        output_line = p.stdout.split("\n")[-2]
        total_size_in_bytes = int(output_line.split(":")[1].lstrip())
    except IndexError:
        logger.error(f"Failed on {full_s3_uri}")
        total_size_in_bytes = 0
        pass

    return total_size_in_bytes


@click.command()
def main():
    logging.basicConfig(level=logging.INFO)

    accession_ids = get_all_study_identifiers()

    for accession_id in accession_ids:
        study = load_and_annotate_study(accession_id)

        for image in study.images.values():
            ome_ngff_rep = get_ome_ngff_rep(image)

            if ome_ngff_rep:
                if ome_ngff_rep.size == 0:
                    logger.info(f"No size information for {ome_ngff_rep.accession_id}:{ome_ngff_rep.image_id}")
                    full_uri = ome_ngff_rep.uri
                    size_in_bytes = full_s3_uri_to_size_in_bytes(full_uri)
                    ome_ngff_rep.size = size_in_bytes
                    persist_image_representation(ome_ngff_rep)





if __name__ == "__main__":
    main()