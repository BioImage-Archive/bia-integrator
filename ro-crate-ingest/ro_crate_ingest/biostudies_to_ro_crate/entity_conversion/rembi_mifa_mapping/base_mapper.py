import logging
from abc import ABC, abstractmethod

from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel

from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Submission,
)

logger = logging.getLogger("__main__." + __name__)


class Mapper(ABC):

    mapped_object: list[ROCrateModel]

    def __init__(self) -> None:
        self.mapped_object = []

        super().__init__()

    @abstractmethod
    def map(
        self, submission: Submission, association_map: dict[type, dict[str, str]]
    ) -> None:
        raise NotImplementedError

    def get_mapped_objects(
        self, submission: Submission, association_map: dict[type, dict[str, str]]
    ) -> list[ROCrateModel]:
        self.map(submission, association_map)
        return self.mapped_object
