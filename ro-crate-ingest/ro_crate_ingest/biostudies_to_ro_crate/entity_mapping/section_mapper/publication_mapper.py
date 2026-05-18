import logging
from urllib.parse import quote

from bia_ro_crate.models import ro_crate_models
from pydantic import AnyUrl

from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Section,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    attributes_to_dict,
)

from .base_section_mapper import SectionMapper

logger = logging.getLogger("__main__." + __name__)


class PublicationMapper(SectionMapper):

    section_type = "publication"
    bnode_int: int

    def __init__(self) -> None:
        self.bnode_int = 0
        super().__init__()

    def get_mapped_object(
        self, section: Section, association_map: dict[type, dict[str, str]]
    ):
        attributes: dict = attributes_to_dict(section.attributes)
        publication_dict = {
            "@id": self.create_id(section),
            "@type": ["ScholarlyArticle", "bia:Publication"],
            "doi": attributes.get("doi"),
            "pubmedId": attributes.get("pubmed_id"),
            "name": attributes.get("title"),
            "yearPublished": attributes.get("year"),
            "authorNames": attributes.get("authors"),
        }

        return ro_crate_models.Publication(**publication_dict)

    def skip_object(self, ro_crate_object: ro_crate_models.ROCrateModel):
        if not isinstance(ro_crate_object, ro_crate_models.Publication):
            return True
        return not any(
            (ro_crate_object.doi, ro_crate_object.pubmedId, ro_crate_object.name)
        )

    def create_id(self, section: Section) -> str:
        # This should try to use a doi or full link using pubmed id, but that isn't necessary and difficult to validate into a correct url.
        if section.accno:
            id = f"#{quote(section.accno)}"
        else:
            id = f"_:p{self.bnode_int}"
            self.bnode_int += 1
        return id
