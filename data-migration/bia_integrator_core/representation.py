import logging
from typing import List

from bia_integrator_core.config import settings
from bia_integrator_core.models import BIAImageRepresentation


logger = logging.getLogger(__name__)
    

def persist_image_representation(representation: BIAImageRepresentation):
    """Persist the representation to disk."""

    representation_dirpath = settings.representations_dirpath/representation.accession_id/representation.image_id
    representation_dirpath.mkdir(exist_ok=True, parents=True)

    representation_fpath = representation_dirpath/f"{representation.type}.json"

    logger.info(f"Writing image representation to {representation_fpath}")
    with open(representation_fpath, "w") as fh:
        fh.write(representation.json(indent=2))


def get_representations(accession_id: str, image_id: str) -> List[BIAImageRepresentation]:
    """Return all representations stored on disk for the given accession/image."""
    
    image_reps_dirpath = settings.representations_dirpath/accession_id/image_id
    if image_reps_dirpath.exists():
        image_reps = [
            BIAImageRepresentation.parse_file(fp)
            for fp in image_reps_dirpath.iterdir()
            if fp.is_file()
        ]
    else:
        image_reps = []

    return image_reps