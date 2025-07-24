from bia_shared_datamodels.ro_crate_models import Contributor
from ro_crate_ingest.empiar_to_ro_crate.empiar.entry_api_models import (
    Entry,
    AuthorEditor,
)

CONTRIBUTOR_BNODE_INT = 0


def get_contributors(empiar_api_entry: Entry) -> list[Contributor]:
    contributors = []
    for author in empiar_api_entry.authors:
        contributors.append(get_contributor(author.author))
    return contributors


def get_contributor(author: AuthorEditor) -> Contributor:
    model_dict = {
        "@type": ["Person", "bia:Contributor"],
        "@id": get_contributor_id(author),
        "displayName": author.name,
        "address": None,
        "website": None,
        "affiliation": [],
        "role": [],
        "contactEmail": None,
    }

    return Contributor(**model_dict)


def get_contributor_id(author: AuthorEditor):

    if author.author_orcid:
        id: str = author.author_orcid
        if not id.startswith("https://orcid.org/"):
            id = f"https://orcid.org/{id}"
    else:
        global CONTRIBUTOR_BNODE_INT
        id = f"_:c{CONTRIBUTOR_BNODE_INT}"
        CONTRIBUTOR_BNODE_INT += 1

    return id
