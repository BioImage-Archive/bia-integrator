import logging
from typing import List

from .models import BIAImage
from .config import settings

logger = logging.getLogger(__name__)


def persist_image(image: BIAImage):
    """Persist the image to disk."""

    image_dirpath = settings.images_dirpath/image.accession_id
    image_dirpath.mkdir(exist_ok=True, parents=True)

    image_fpath = image_dirpath/f"{image.id}.json"

    logger.info(f"Writing image to {image_fpath}")
    with open(image_fpath, "w") as fh:
        fh.write(image.json(indent=2))


def get_images(accession_id: str) -> List[BIAImage]:
    """Return all images stored on disk for the given accession."""
    
    images_dirpath = settings.images_dirpath/accession_id
    if images_dirpath.exists():
        images_list = [
            BIAImage.parse_file(fp)
            for fp in images_dirpath.iterdir()
            if fp.is_file()
        ]
    else:
        images_list = []

    return {image.id: image for image in images_list}