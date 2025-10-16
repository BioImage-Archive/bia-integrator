from typing import Optional
from pydantic import BaseModel, Field


class Imageset(BaseModel):
    name: str = Field(description="The name of the imageset.")
    directory: str = Field(description="The directory where the imageset is located.")
    category: Optional[str] = Field(
        None, description="The category to which the imageset belongs."
    )
    header_format: Optional[str] = Field(
        None, description="The format of the headers of the data in the imageset."
    )
    data_format: Optional[str] = Field(
        None, description="The format of the data in the imageset."
    )
    num_images_or_tilt_series: Optional[float] = Field(
        None, description="The number of images or tilt series in the imageset."
    )
    frames_per_image: Optional[float] = Field(
        None, description="The number of frames per image."
    )
    frame_range_min: Optional[float] = Field(
        None,
        description="The minimum index of the frames if the imageset consists of a range of images.",
    )
    voxel_type: Optional[str] = Field(
        None, description="The type of voxels in the images."
    )
    pixel_width: Optional[float] = Field(
        None, description="The width of pixels in the imageset."
    )
    pixel_height: Optional[float] = Field(
        None, description="The height of pixels in the imageset."
    )
    details: Optional[str] = Field(
        None, description="Additional information about the imageset."
    )
    image_width: Optional[str] = Field(
        None, description="The width of images in the imageset."
    )
    image_height: Optional[str] = Field(
        None, description="The height of images in the imageset."
    )
    micrographs_file_pattern: Optional[str] = Field(
        None,
        description="The pattern for the micrographs that correspond to the picked particles.",
    )
    picked_particles_file_pattern: Optional[str] = Field(
        None,
        description="The pattern for the picked particle description files or the path to such a file if there is just one.",
    )
    picked_particles_directory: Optional[str] = Field(
        None, description="The directory that contains the related picked particles."
    )


class WorkflowFile(BaseModel):
    workflow_file: Optional[str] = Field(
        None,
        description="Workflow file provides a great way to reproduce previous processing steps and is particularly useful to repeat steps for similar samples or to share knowledge between users.",
    )


class GrantReference(BaseModel):
    funding_body: Optional[str] = Field(
        None, description="The name of the funding body."
    )
    code: Optional[str] = Field(None, description="The code of the grant reference.")
    country: Optional[str] = Field(None, description="The country of the funding body.")


class VersionHistory(BaseModel):
    version_number: Optional[float] = Field(
        None, description="The version number of the entry in the version history."
    )
    date: Optional[str] = Field(
        None, description="The date on which the entry has been updated."
    )
    status_code: Optional[str] = Field(
        None,
        description="The status code of the entry at the moment it has been updated.",
    )
    details: Optional[str] = Field(None, description="Details of the entry update.")


class AuthorDetailed(BaseModel):
    author_orcid: Optional[str] = Field(None, description="The ORCID ID of the author.")
    middle_name: Optional[str] = Field(
        None, description="The middle name of the author."
    )
    organization: Optional[str] = Field(
        None, description="The organization the author belongs to."
    )
    street: Optional[str] = Field(
        None, description="The street on which the organization is located."
    )
    town_or_city: Optional[str] = Field(
        None, description="The town or city where the organization is located."
    )
    state_or_province: Optional[str] = Field(
        None, description="The state or province where the organization is located."
    )
    post_or_zip: Optional[str] = Field(
        None, description="The post or zip of the organization."
    )
    telephone: Optional[str] = Field(
        None, description="The telephone by which the author can be reached."
    )
    fax: Optional[str] = Field(
        None, description="The fax by which the author can be reached."
    )
    first_name: Optional[str] = Field(None, description="The first name of the author.")
    last_name: Optional[str] = Field(None, description="The last name of the author.")
    email: Optional[str] = Field(None, description="The email address the author.")
    country: Optional[str] = Field(
        None, description="The country where the organization is located."
    )


class AuthorEditor(BaseModel):
    name: Optional[str] = Field(
        None,
        description="The name of the author or editor. Consists of the last name and initials.",
    )
    author_orcid: Optional[str] = Field(None, description="The ORCID ID of the author.")


class EntryAuthor(BaseModel):
    author: AuthorEditor


class CorrespondingAuthor(BaseModel):
    author: AuthorDetailed


class CrossReference(BaseModel):
    name: Optional[str] = Field(None, description="The refernce code")


class Citation(BaseModel):
    authors: list[AuthorEditor] = Field(
        default_factory=list,
        description="The authors of the citation. Could differ from those of the EMPIAR entry",
    )
    editors: list[AuthorEditor] = Field(
        default_factory=list,
        description="The editors of the citation. Could differ from those of the EMPIAR entry",
    )
    published: Optional[bool] = Field(
        None, description="True if the citation has been published, otherwise false"
    )
    j_or_nj_citation: bool = Field(
        description="True if the citation is a journal publication, otherwise false",
    )
    title: Optional[str] = Field(None, description="The title of the citation")
    volume: Optional[str] = Field(None, description="The volume of the citation")
    country: Optional[str] = Field(
        None, description="The country where the citation has been published"
    )
    first_page: Optional[str] = Field(
        None, description="The first page of the citation"
    )
    last_page: Optional[str] = Field(None, description="The last page of the citation")
    year: Optional[str] = Field(
        None, description="The year of the publication of the citation"
    )
    language: Optional[str] = Field(None, description="The language of the citation")
    doi: Optional[str] = Field(None, description="The DOI of the citation")
    pubmedid: Optional[str] = Field(None, description="The PubMed ID of the citation")
    details: Optional[str] = Field(
        None, description="Additional details about the citation"
    )
    book_chapter_title: Optional[str] = Field(
        None, description="The title of the book chapter of the citation"
    )
    publisher: Optional[str] = Field(None, description="The publishing body")
    publication_location: Optional[str] = Field(
        None, description="The location of the publication"
    )
    journal: Optional[str] = Field(
        None, description="The journal where the citation is published"
    )
    journal_abbreviation: Optional[str] = Field(
        None, description="The abbreviation name of the journal"
    )
    issue: Optional[str] = Field(None, description="The citation's issue")


class Entry(BaseModel):
    id: Optional[str] = Field(
        None, description="Unique identifier representing a specific EMPIAR entry."
    )
    imagesets: list[Imageset] = Field(
        default_factory=list,
        description="The image sets that are stored in the EMPIAR entry.",
    )
    version_history: list[VersionHistory] = Field(
        default_factory=list,
        description="The history of the changes of the EMPIAR entry.",
    )
    title: str = Field(description="The EMPIAR entry title.")
    principal_investigator: list[AuthorDetailed] = Field(
        default_factory=list,
        description="One or more principal investigator investigators.",
    )
    status: Optional[str] = Field(
        None, description="Status of the entry. Can be released or obsoleted."
    )
    deposition_date: Optional[str] = Field(
        None, description="The date on which the entry has been deposited."
    )
    release_date: Optional[str] = Field(
        None, description="The date on which the entry has been released."
    )
    obsolete_date: Optional[str] = Field(
        None, description="The date on which the entry has been obsoleted."
    )
    update_date: Optional[str] = Field(
        None, description="The date on which the entry has had the last update."
    )
    corresponding_author: CorrespondingAuthor = Field()
    authors: list[EntryAuthor] = Field(
        default_factory=list, description="Complete list of the entry authors."
    )
    cross_references: list[str] = Field(
        default_factory=list,
    )
    grant_references: list[GrantReference] = Field(
        default_factory=list,
        description="The grant references that are related to the EMPIAR entry.",
    )
    citation: list[Citation] = Field(
        default_factory=list,
        description="The citation information related to the EMPIAR entry.",
    )
    dataset_size: Optional[str] = Field(
        None, description="The size of the EMPIAR entry"
    )
    experiment_type: Optional[str] = Field(
        None,
        description="The type of the EMPIAR entry. Can be SBF-SEM, INSILICO, EMDB, SXT, FIB-SEM, IHM, CLEM, CLXM, MicroED, ATUM-SEM, Hard X-ray/X-ray microCT, ssET.",
    )
    scale: Optional[str] = Field(
        None,
        description="The scale of the EMPIAR entry. Can be molecule, cell, tissue, organism.",
    )
    entry_doi: Optional[str] = Field(
        None, description="The Digital Object Identifier (DOI) of the EMPIAR entry."
    )
    biostudies_references: list[CrossReference] = Field(
        default_factory=list,
    )
    idr_references: list[CrossReference] = Field(
        default_factory=list,
    )
    empiar_references: list[CrossReference] = Field(
        default_factory=list,
    )


class LatestCitation(BaseModel):
    pmid: Optional[str] = Field(None, description="PubMed identifier of the citation.")
    pub_year: Optional[str] = Field(
        None, description="The year in which the citation was published."
    )
    author_string: Optional[str] = Field(
        None, description="The list of the citation authors"
    )
    title: Optional[str] = Field(None, description="The title of the citation.")
