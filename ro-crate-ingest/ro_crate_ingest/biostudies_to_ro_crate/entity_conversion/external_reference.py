import logging

from bia_shared_datamodels import ro_crate_models
from pydantic import AnyUrl

from ro_crate_ingest.biostudies_to_ro_crate.biostudies.constants import (
    ALLOWED_LINK_TYPES,
    URL_TEMPLATES,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Empty,
    Submission,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    attributes_to_dict,
)

logger = logging.getLogger("__main__." + __name__)


def sanitise_link_and_link_type(
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
        


def get_external_references(
    submission: Submission,
) -> list[ro_crate_models.ExternalReference]:

    links = submission.section.links

    external_references = list()
    for biostudies_link in links:
        if isinstance(biostudies_link, Empty) or biostudies_link.url is None:
            continue

        attributes: dict = attributes_to_dict(biostudies_link.attributes)

        link, link_type = sanitise_link_and_link_type(
            biostudies_link.url, attributes.get("type")
        )
        logger.warning(link)

        if not link:
            continue

        external_references.append(ro_crate_models.ExternalReference.model_validate(
            {
                "@id": link,
                "@type": "bia:ExternalReference",
                "description": attributes.get("description"),
                "additionalType": link_type,
            }
        ))

    return external_references
