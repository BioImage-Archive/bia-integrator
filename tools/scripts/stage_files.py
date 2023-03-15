import logging
from pathlib import Path
from urllib.parse import urlparse

import typer
from bia_integrator_core.integrator import load_and_annotate_study

from bia_integrator_tools.io import copy_uri_to_local


logger = logging.getLogger(__file__)


def get_image_rep_by_type(accession_id, image_id, rep_type):

    bia_study = load_and_annotate_study(accession_id)

    for image_rep in bia_study.images[image_id].representations:
        if image_rep.type == rep_type:
            return image_rep

    return None


def main(accession_id: str, image_id: str, rep_type: str):
    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)
    image_rep = get_image_rep_by_type(accession_id, image_id, rep_type)

    print(image_rep)

    cache_root_dirpath = Path.home()/".cache"/"bia-converter"
    cache_dirpath = cache_root_dirpath/accession_id
    cache_dirpath.mkdir(exist_ok=True, parents=True)

    for fileref_id in image_rep.attributes["fileref_ids"]:
        fileref = bia_study.file_references[fileref_id]
        suffix = Path(urlparse(fileref.uri).path).suffix
        dst_fname = fileref_id+suffix
        dst_fpath = cache_dirpath/dst_fname
        logger.info(f"Checking cache for {fileref.name}")

        if not dst_fpath.exists():
            copy_uri_to_local(fileref.uri, dst_fpath)
            logger.info(f"Downloading file to {dst_fpath}")
        else:
            logger.info(f"File exists at {dst_fpath}")


if __name__ == "__main__":
    typer.run(main)