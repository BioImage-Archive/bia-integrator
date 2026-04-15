import re
from urllib.parse import quote

from bia_shared_datamodels.ro_crate_models import Publication

from ro_crate_ingest.empiar_to_ro_crate.empiar.proposal import Proposal

DOI_PATTERN = re.compile(r'^10\.\d{4,}/')


def get_publications(
    proposal: Proposal
) -> list[Publication]:
    
    publication_bnode_int = 0
    publications = []
    yaml_publication_dois = proposal.paper_doi
    for publication_doi in yaml_publication_dois:
        publication, publication_bnode_int = get_publication(
            publication_doi, publication_bnode_int
        )
        publications.append(publication)
    
    return publications


def get_publication(
    publication_doi: str, publication_bnode_int: int
) -> tuple[Publication, int]:

    publication_id, publication_bnode_int = get_publication_id(
        publication_doi, publication_bnode_int
    )

    model_dict = {
        "@id": publication_id,
        "@type": ["ScholarlyArticle", "bia:Publication"],
        "doi": publication_doi.removeprefix("https://doi.org/"),
    }

    return Publication(**model_dict), publication_bnode_int


def get_publication_id(
    publication_doi: str, publication_bnode_int: int
) -> tuple[str, int]:
    
    if publication_doi.startswith("https://doi.org/"):
        publication_doi = publication_doi.removeprefix("https://doi.org/")
    if not DOI_PATTERN.match(publication_doi):
        raise ValueError(f"Expected a DOI, got: {publication_doi}")
    return f"https://doi.org/{quote(publication_doi)}", publication_bnode_int
