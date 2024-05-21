from typing import List

from pydantic import BaseModel


class Affiliation(BaseModel):
    name: str
    rorid: str | None


class Author(BaseModel):
    name: str
    email: str | None
    orcid: str | None
    affiliation: Affiliation
    role: str | None


class Publication(BaseModel):
    title: str
    authors: str | None
    doi: str | None
    year: str | None
    pubmed_id: str | None


class BIAStudy(BaseModel):
    accession_id: str
    title: str
    description: str
    release_date: str
    funding: str
    license: str = "CC0"
    keywords: List[str] = []
    authors: List[Author] = []
    publications: List[Publication] = []
