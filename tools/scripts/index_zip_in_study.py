import hashlib
import logging
from urllib.parse import urlparse
from pathlib import Path
from zipfile import ZipFile

import click

from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.interface import persist_study
from bia_integrator_core.models import BIAFile, BIAImageRepresentation, BIAImage

from bst_pulldown import IMAGE_EXTS

logger = logging.getLogger(__file__)


def fetch_zipfile_with_caching(zipfile: BIAFile) -> Path:

    # FIXME - not always first representation
    zipfile_rep = zipfile.representations[0]
    cache_dirpath = Path.home()/".cache"/"bia-converter"
    cache_dirpath.mkdir(exist_ok=True, parents=True)

    suffix = Path(urlparse(zipfile_rep.uri).path).suffix
    prefix = hashlib.md5(zipfile_rep.uri.encode()).hexdigest()
    dst_fname = prefix + suffix
    dst_fpath = cache_dirpath/dst_fname
    
    if not dst_fpath.exists():
        copy_uri_to_local(zipfile_uri, dst_fpath)
        logger.info(f"Downloading zipfile to {dst_fpath}")
    else:
        logger.info(f"Zipfile exists at {dst_fpath}")

    return dst_fpath
    

@click.command()
@click.argument('accession_id')
@click.argument('zipfile_id')
def main(accession_id, zipfile_id):

    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)

    zipfile = bia_study.archive_files[zipfile_id]
    zipfile_fpath = fetch_zipfile_with_caching(zipfile)

    with ZipFile(zipfile_fpath) as zipf:
        info_list = zipf.infolist()

    image_zipinfos = [
        zipinfo for zipinfo in info_list
        if Path(zipinfo.filename).suffix in IMAGE_EXTS
    ]

    images = {}
    for n, zipinfo in enumerate(image_zipinfos, start=1):

        image_id = f"{zipfile_id}-IM{n}"

        rep = BIAImageRepresentation(
            accession_id=accession_id,
            image_id=image_id,
            # FIXME
            uri=zipfile.representations[0].uri,
            size=zipinfo.file_size,
            type="zipfile",
            attributes = {"zip_filename": zipinfo.filename}
        )

        images[image_id] = BIAImage(
            id=image_id,
            original_relpath=zipinfo.filename,
            representations=[rep]
        )

    bia_study.images.update(images)
    persist_study(bia_study)

    


if __name__ == "__main__":
    main()