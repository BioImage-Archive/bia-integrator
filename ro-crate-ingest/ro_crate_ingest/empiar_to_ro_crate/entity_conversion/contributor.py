from bia_shared_datamodels.ro_crate_models import Contributor
from ro_crate_ingest.empiar_to_ro_crate.empiar.entry_api_models import (
    Entry,
    AuthorEditor,
)


def get_contributors(empiar_api_entry: Entry) -> list[Contributor]:
    contributors = []
    for author in empiar_api_entry.authors:
        contributors.append(get_contributor(author.author))
    return contributors


def get_contributor(author: AuthorEditor) -> Contributor:
    model_dict = {
        "@type": ["Person", "bia:Contributor"],
        "@id": author.author_orcid,
        "displayName": author.name,
        "address": None,
        "website": None,
        "affiliation": [],
        "role": [],
        "contactEmail": None,
    }

    return Contributor(**model_dict)
