import logging
from typing import List

from bia_integrator_core.config import settings
from bia_integrator_core.models import BIAImageAlias


logger = logging.getLogger(__name__)
    

def persist_image_alias(alias: BIAImageAlias):
    """Persist the alias to disk."""

    obj = alias

    persistence_dirpath = settings.aliases_dirpath/alias.accession_id
    persistence_dirpath.mkdir(exist_ok=True, parents=True)

    persistence_fpath = persistence_dirpath/f"{alias.image_id}-{alias.name}.json"

    logger.info(f"Writing image alias to {persistence_fpath}")
    with open(persistence_fpath, "w") as fh:
        fh.write(obj.json(indent=2))


def get_aliases(accession_id: str) -> List[BIAImageAlias]:
    """Return all aliases stored on disk for the given accession/image."""
    
    obj_class = BIAImageAlias
    persistence_dirpath = settings.aliases_dirpath/accession_id
    if persistence_dirpath.exists():
        retrieved = [
            obj_class.parse_file(fp)
            for fp in persistence_dirpath.iterdir()
            if fp.is_file()
        ]
    else:
        retrieved = []

    return retrieved