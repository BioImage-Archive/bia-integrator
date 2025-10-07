from bia_shared_datamodels.ro_crate_models import Contributor
from ro_crate_ingest.empiar_to_ro_crate.empiar.entry_api_models import (
    Entry,
    AuthorEditor,
)


def get_contributors(empiar_api_entry: Entry) -> list[Contributor]:
    contributor_bnode_int = 0
    contributors = []
    for author in empiar_api_entry.authors:
        contributor, contributor_bnode_int = get_contributor(
            author.author, contributor_bnode_int
        )
        contributors.append(contributor)
    return contributors


def get_contributor(author: AuthorEditor, contributor_bnode_int: int) -> tuple[Contributor, int]:
    contributor_id, contributor_bnode_int = get_contributor_id(
        author, contributor_bnode_int
    )

    model_dict = {
        "@type": ["Person", "bia:Contributor"],
        "@id": contributor_id,
        "displayName": author.name,
        "address": None,
        "website": None,
        "affiliation": [],
        "role": [],
        "contactEmail": None,
    }

    return Contributor(**model_dict), contributor_bnode_int


def get_contributor_id(
    author: AuthorEditor, contributor_bnode_int: int
) -> tuple[str, int]:

    if author.author_orcid:
        id: str = author.author_orcid
        if not id.startswith("https://orcid.org/"):
            id = f"https://orcid.org/{id}"
    else:
        id = f"_:c{contributor_bnode_int}"
        contributor_bnode_int += 1

    return id, contributor_bnode_int
