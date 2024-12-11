from typing import Dict, List
from bia_shared_datamodels import bia_data_model, semantic_models
from bia_shared_datamodels.uuid_creation import create_study_uuid
from .mock_object_constants import accession_id


def get_affiliation() -> Dict[str, semantic_models.Affiliation]:
    affiliation1 = semantic_models.Affiliation.model_validate(
        {
            "display_name": "Test College 1",
            "rorid": None,
            "address": None,
            "website": None,
        }
    )
    affiliation2 = semantic_models.Affiliation.model_validate(
        {
            "display_name": "Test College 2",
            "rorid": None,
            "address": None,
            "website": None,
        }
    )
    return {
        "o1": affiliation1,
        "o2": affiliation2,
    }


def get_contributor() -> List[semantic_models.Contributor]:
    affiliations = get_affiliation()
    contributor1 = semantic_models.Contributor.model_validate(
        {
            "display_name": "Test Author1",
            "contact_email": "test_author1@ebi.ac.uk",
            "role": "corresponding author",
            "affiliation": [
                affiliations["o1"],
            ],
            "rorid": None,
            "address": None,
            "website": None,
            "orcid": "0000-0000-0000-0000",
        }
    )
    contributor2 = semantic_models.Contributor.model_validate(
        {
            "display_name": "Test Author2",
            "contact_email": "test_author2@ebi.ac.uk",
            "role": "first author",
            "affiliation": [
                affiliations["o2"],
            ],
            "rorid": None,
            "address": None,
            "website": None,
            "orcid": "1111-1111-1111-1111",
        }
    )

    return [
        contributor1,
        contributor2,
    ]


def get_publication() -> List[semantic_models.Publication]:
    publication1 = semantic_models.Publication.model_validate(
        {
            "pubmed_id": "38381674",
            "title": "Test publication 1",
            # TODO: No release date -> ST only collects Year
            "release_date": "2024",
            # TODO: Author is a string here.
            "author": "Test Author11, Test Author12.",
        }
    )
    publication2 = semantic_models.Publication.model_validate(
        {
            "pubmed_id": "38106175",
            "doi": "10.1101/2023.12.07.570699",
            "title": "Test publication 2",
            # TODO: Author is a string here.
            "author": "Test Author21, Test Author22",
            "release_date": "2023",
        }
    )
    return [
        publication1,
        publication2,
    ]


def get_external_reference() -> List[semantic_models.ExternalReference]:
    link1 = semantic_models.ExternalReference.model_validate(
        {
            "link": "https://www.test.link1.com/",
            "description": "Test link 1.",
        }
    )
    link2 = semantic_models.ExternalReference.model_validate(
        {
            "link": "ERP116793",
            "description": "Test ENA link",
            "Type": "ENA",
        }
    )
    return [
        link1,
        link2,
    ]


def get_grant() -> List[semantic_models.Grant]:
    funding_body1 = semantic_models.FundingBody.model_validate(
        {
            "display_name": "Test funding body1",
        }
    )
    funding_body2 = semantic_models.FundingBody.model_validate(
        {
            "display_name": "Test funding body2",
        }
    )

    grant1 = semantic_models.Grant.model_validate(
        {
            "id": "TESTFUNDS1",
            "funder": [
                funding_body1,
            ],
        }
    )
    grant2 = semantic_models.Grant.model_validate(
        {
            "id": "TESTFUNDS2",
            "funder": [
                funding_body2,
            ],
        }
    )
    return [
        grant1,
        grant2,
    ]


def get_study() -> bia_data_model.Study:
    contributor = get_contributor()
    grant = get_grant()
    study_dict = {
        "uuid": create_study_uuid(accession_id),
        "accession_id": accession_id,
        "title": "A test submission with title greater than 25 characters",
        "description": "A test submission to allow testing without retrieving from bia server",
        "release_date": "2024-02-13",
        "licence": semantic_models.LicenceType.CC0,
        "acknowledgement": "We thank you",
        "funding_statement": "This work was funded by the EBI",
        "attribute": [
            {
                "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                "name": "Extras from biostudies.Submission.attributes",
                "value": {
                    "Extra attribute 1": "Extra attribute 1 to test semantic_model.study.attribute",
                },
            },
            {
                "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                "name": "Extras from biostudies.Submission.attributes",
                "value": {
                    "Extra attribute 2": "Extra attribute 2 to test semantic_model.study.attribute",
                },
            },
            {
                "provenance": semantic_models.AttributeProvenance("bia_ingest"),
                "name": "biostudies json/pagetab entry",
                "value": {
                    "json": f"https://www.ebi.ac.uk/biostudies/files/{accession_id}/{accession_id}.json",
                    "pagetab": f"https://www.ebi.ac.uk/biostudies/files/{accession_id}/{accession_id}.tsv",
                },
            },
        ],
        "related_publication": [],
        "author": [c.model_dump() for c in contributor],
        "keyword": [
            "Test keyword1",
            "Test keyword2",
            "Test keyword3",
        ],
        "grant": [g.model_dump() for g in grant],
        "version": 0,
    }
    study = bia_data_model.Study.model_validate(study_dict)
    return study
