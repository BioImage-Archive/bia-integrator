from __future__ import annotations

from enum import Enum
from datetime import date
from typing import (
    List,
    Dict,
    Optional,
)

from pydantic import BaseModel, Field, EmailStr, AnyUrl

from uri import URI


# Agentive classes: e.g. people, organisations, grants.


class Agent(BaseModel):
    """
    A resource that acts or has the power to act.
    """

    display_name: str = Field(
        description="""Name as it should be displayed on the BioImage Archive."""
    )
    contact_email: EmailStr = Field(
        description="""An email address to contact the person or organisation"""
    )
    memberOf: Optional[List[Organisation]] = Field(
        default_factory=list,
        description="""The organisations an Agent is afiliated with.""",
    )


class Organisation(Agent):
    """
    An Agent that is composed of multiple members established to meet needs or persue goals.
    """

    rorid: Optional[str] = Field(
        None, description="""Reasearch Organisation Registry ID"""
    )
    address: Optional[str] = Field(
        None, description="""Comma separated lines of the address."""
    )


class Person(Agent):
    """
    A human being.
    """

    orcid: Optional[str] = Field(
        None, description="""Open Researcher and Contributor ID"""
    )


class Grant(BaseModel):
    """ """

    id: Optional[str] = Field(
        None,
        description="""A unique identifier for the grant, such as an Open Funder Registry ID.""",
    )

    funder: List[Agent] = Field(
        default_factory=list,
        description="""The funding body provididing support to a grant.""",
    )


# Document classes: e.g. studies and publications.


class Document(BaseModel):
    """
    A documentary resource or body of scientific work.
    """

    author: List[Agent] = Field(description="""The creators of the document.""")
    title: str = Field(
        description="""The title of a scientific document. This will usually be displayed when search results including your data are shown."""
    )
    release_date: date = Field(description="""Date of first publication""")
    keywords: Optional[List[str]] = Field(
        default_factory=list,
        description="""Keywords or tags used to describe the subject of a document""",
    )
    acknowledgements: Optional[List[Agent]] = Field(
        default_factory=list,
        description="""Any person or group that should be acknowledged with the document.""",
    )
    description: Optional[str] = Field(
        None, description="""Brief description of the scientific document."""
    )


class Study(Document):
    """
    A study in the BioImageArchive represents a set of image data, and the scienfitic effort that resulted in its creation.
    """

    accession_id: str = Field(description="""Unique ID provided by BioStudies.""")
    file_reference_count: int = Field(
        description="""Number of files associated with the study."""
    )
    image_count: int = Field(
        description="""Number of images associated with the study."""
    )
    see_also: Optional[List[AnyUrl]] = Field(
        default_factory=list,
        description="""Links to publications, github repositories, and other pages related to this Study.""",
    )
    fundedBy: Optional[Grant] = Field(
        None, description="""The grants that funded the study."""
    )
    part: Optional[List[StudyComponent]] = Field(
        default_factory=list,
        description="""A related document that is included logically in the described document.""",
    )


class Publication(Document):
    """
    A published paper or written work.
    """

    pubmed_id: Optional[str] = Field(
        None, description="""Identifier for journal articles/abstracts in PubMed"""
    )
    doi: str = Field(description="""Digital Object Identifier (DOI)""")


class StudyComponent:
    """
    A locigal grouping of the data associated with a Study.
    """

    pass


# Image classes: e.g. Images, how they were created, what is their subject.


class Image(BaseModel):
    """
    The abstraction of an image, which can be represented by individual image files.
    """

    represenatation: List[ImageRepresentation] = Field(
        description="""The files that store the image data."""
    )
    acquisition_process: List[ImageAcquisition] = Field(
        description="""The processes involved in the creation of the image."""
    )


class ImageAcquisition(BaseModel):
    """
    The process through which an image is captured.
    """

    subject: List[Specimen] = Field(
        description="""The Specimens that were the subject of the image acquisition process."""
    )
    fbbi_id: str = Field(
        description="""Biological Imaging Methods Ontology id indicating the kind of imaging that was perfomed."""
    )
    imaging_method_description: str = Field(
        description="""A description of how the images were taken."""
    )
    imaging_instrument_description: str = Field(
        description="""Names, types, or description of how the instruments used to create the image."""
    )
    image_acquistion_parameters: str = Field(
        description="""Parameters relevant to how the image was taken, such as instrument settings."""
    )


class Specimen(BaseModel):
    """
    The subject of an image acquisition.
    """

    sampleOf: List[Biosample] = Field(
        description="""The biological matter that sampled to create the specimen."""
    )
    sample_preparation_description: Optional[str] = Field(
        None, description="""The process by which the specimen was created"""
    )
    signal_contrast_mechanism_description: Optional[str] = Field(
        None, description="""How is the signal generated by this sample"""
    )
    growth_protocol_description: Optional[str] = Field(
        None, description="""placeholder"""
    )
    channel_content_description: Optional[str] = Field(
        None,
        description="""What staining was used in preparation of the specimen (e.g. IEM, DAB).""",
    )
    channel_biological_entity: Optional[str] = Field(
        None, description="""What molecule is stained."""
    )


class Biosample(BaseModel):
    """
    THe biological entity that has undergone preparation (as a Sample) in order to be imaged.
    """

    organism: List[Taxon] = Field(
        description="""The biological matter that sampled to create the specimen."""
    )
    description: str = Field(
        description="""A short description of the biological entity."""
    )
    experimental_variable_description: Optional[List[str]] = Field(
        description="""What is intentionally varied (e.g. time) between multiple entries in this study component"""
    )
    extrinsic_variable_description: Optional[List[str]] = Field(
        description="External treatment (e.g. reagent)."
    )
    intrinsic_variable_description: Optional[List[str]] = Field(
        description="Intrinsic (e.g. genetic) alteration."
    )


class Taxon(BaseModel):
    """
    The classification of a biological entity.
    """

    common_name: Optional[str] = Field(None)
    scientific_name: Optional[str] = Field(None)
    ncbi_id: Optional[str] = Field(None)


# File classes: Files, image files & their channels


class FileReference(BaseModel):
    """
    The digital represenation of a document.
    """

    name: str = Field(description="""The name of the file.""")
    format: str = Field(description="""File format or type.""")
    size_in_bytes: int = Field(description="""Disc size in bytes.""")
    uri: URI = Field(description="""URI from which the file can be accessed.""")


class ImageRepresentation(FileReference):
    """
    The manifestation of an image in a particular image file format.
    """

    physical_dimension: Optional[str] = Field(
        None, description="""Size of the physical space captured by the image"""
    )
    digital_dimension: Optional[str] = Field(
        None, description="""Size in pixels or voxels of the image"""
    )
    image_viewer_setting: Optional[RenderedView] = Field(
        None,
        description="""Settings of a particular view of an image, such as a specific timestamp of a timeseries, or camera placement in a 3D model.""",
    )


class RenderedView(BaseModel):
    """
    A particular view of an image, such as as a specific timestamp of a time series, or a view direction of a 3D model
    """

    z: Optional[str] = Field(
        None, description="""A z-value for the position of the image view"""
    )
    t: Optional[str] = Field(
        None, description="""A t-value for the timestamp of the image view"""
    )
    channel_information: Optional[List[str]] = Field(
        None,
        description="""Information about the channels involved in displaying this view of the image.""",
    )


class Channel(BaseModel):
    """
    An image channel
    """

    colormap_start: float = Field(description="""Start value of colormap""")
    colormap_end: float = Field(description="""End value of colormap""")
    scale_factor: float = Field(None)
    label: Optional[str] = Field(
        None, description="""Label describing the channel for display."""
    )
