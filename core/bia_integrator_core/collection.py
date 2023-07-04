import logging

from .config import settings
from openapi_client import models as api_models


logger = logging.getLogger(__name__)


def get_collection(name: str) -> api_models.BIACollection:
    """Load the collection with the given name from disk and return."""

    return settings.api_client.search_collections_api_collections_get(name=name)
    

def persist_collection(collection: api_models.BIACollection):
    """Persist the given collection to disk."""

    settings.api_client.create_collection_api_private_collections_post(collection)

def update_collection(collection: api_models.BIACollection):
    collection.version += 1
    settings.api_client.create_collection_api_private_collections_post(collection)