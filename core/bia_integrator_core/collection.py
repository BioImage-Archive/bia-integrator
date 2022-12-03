import logging

from .config import Settings
from .models import BIACollection


logger = logging.getLogger(__name__)


def get_collection(name: str) -> BIACollection:
    """Load the collection with the given name from disk and return."""

    settings = Settings()
    collections_dirpath = settings.data_dirpath/"collections"
    collection_fpath = collections_dirpath/f"{name}.json"

    return BIACollection.parse_file(collection_fpath)
    

def persist_collection(collection: BIACollection):
    """Persist the given collection to disk."""

    settings = Settings()
    collections_dirpath = settings.data_dirpath/"collections"
    collections_dirpath.mkdir(exist_ok=True, parents=True)

    collection_fpath = collections_dirpath/f"{collection.name}.json"
    logger.info(f"Writing collection to {collection_fpath}")

    with open(collection_fpath, "w") as fh:
        fh.write(collection.json(indent=2))
