import logging

from bia_ro_crate.models import ro_crate_models
from pydantic import AnyUrl

from ro_crate_ingest.biostudies_to_ro_crate.biostudies.constants import (
    ALLOWED_LINK_TYPES,
    URL_TEMPLATES,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Empty,
    Link,
    Submission,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    attributes_to_dict,
)

from .base_mapper import Mapper

logger = logging.getLogger("__main__." + __name__)


class ExternalReferenceMapper(Mapper):

    def get_study_links(self, submission: Submission):
        return submission.section.links

    def map(self, submission: Submission, association_map: dict[type, dict[str, str]]):

        links = self.get_study_links(submission)

        for link in links:

            if isinstance(link, Empty) or link.url is None:
                continue

            ro_crate_object = self.get_mapped_object(link)

            if ro_crate_object:
                self.mapped_object.append(ro_crate_object)
                association_map[ro_crate_models.ExternalReference][
                    link.url
                ] = ro_crate_object.id

    def get_mapped_object(
        self, biostudies_link: Link
    ) -> ro_crate_models.ExternalReference | None:
        attributes: dict = attributes_to_dict(biostudies_link.attributes)

        if not biostudies_link.url:
            return None

        link, link_type = self._sanitise_link_and_link_type(
            biostudies_link.url, attributes.get("type")
        )

        link_dict = {
            "@id": link,
            "@type": "bia:ExternalReference",
            "description": attributes.get("description"),
            "additionalType": link_type,
        }

        return ro_crate_models.ExternalReference(**link_dict)

    @staticmethod
    def _sanitise_link_and_link_type(
        link_raw: str, link_type_raw: str | None
    ) -> tuple[str | None, str | None]:
        link_raw = link_raw.strip()

        normalised_link_type = None
        if link_type_raw:
            normalised_link_type = str(link_type_raw).strip().lower()

        try:
            parsed_url = AnyUrl(link_raw)
            return str(parsed_url), normalised_link_type
        except:
            if normalised_link_type not in ALLOWED_LINK_TYPES:
                return None, None

            template = URL_TEMPLATES[normalised_link_type]

            expanded_link = template.format(link_raw)

            try:
                parsed_url = AnyUrl(expanded_link)
                return str(parsed_url), normalised_link_type
            except:
                return None, None
