import logging

from .config import settings
from bia_integrator_api import models as api_models
from typing import List

logger = logging.getLogger(__name__)


def get_collection(name: str) -> api_models.BIACollection:
    """Load the collection with the given name from disk and return."""

    return settings.api_client.search_collections(name)[0]

def get_collections() -> List[api_models.BIACollection]:
    return settings.api_client.search_collections()

def persist_collection(collection: api_models.BIACollection):
    """Persist the given collection to disk."""

    settings.api_client.create_collection(collection)

def update_collection(collection: api_models.BIACollection):
    collection.version += 1
    settings.api_client.create_collection(collection)