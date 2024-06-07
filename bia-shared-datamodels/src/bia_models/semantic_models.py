from __future__ import annotations

from enum import Enum
from datetime import date
from typing import Any, List, Literal, Dict, Optional, Union

from pydantic import BaseModel, Field, EmailStr, AnyUrl

# from uri import URI

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
    affiliation: Optional[List[Organisation]] = Field(
        default_factory=list,
        description="""The organisations an Agent is afiliated with.""",
    )
    website: Optional[AnyUrl] = Field(
        default=None,
        description="""The website page with information about the Agent.""",
    )


class Organisation(Agent):
    """
    An Agent that is composed of multiple members established to meet needs or pursue goals.
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
    keyword: Optional[List[str]] = Field(
        default_factory=list,
        description="""Keywords or tags used to describe the subject of a document""",
    )
    acknowledgement: Optional[List[Agent]] = Field(
        default_factory=list,
        description="""Any person or group that should be acknowledged with the document.""",
    )
    description: Optional[str] = Field(
        None, description="""Brief description of the scientific document."""
    )


class Study(Document):
    """
    A piece of scientific work that resulted in the creation of imaging data.
    """

    accession_id: str = Field(description="""Unique ID provided by BioStudies.""")
    file_reference_count: int = Field(
        description="""Number of files associated with the study."""
    )
    image_count: int = Field(
        description="""Number of images associated with the study."""
    )
    license: LicenseType = Field(
        description="""The license under which the data associated with the study is made avaliable."""
    )
    see_also: Optional[List[ExternalReference]] = Field(
        default_factory=list,
        description="""Links to publications, github repositories, and other pages related to this Study.""",
    )
    related_publication: Optional[List[Publication]] = Field(
        description="""The publications that the work involved in the study contributed to."""
    )
    grant: Optional[List[Grant]] = Field(
        default_factory=list, description="""The grants that funded the study."""
    )
    funding_statement: Optional[str] = Field(
        default_factory=list, description="""Description of how the study was funded"""
    )
    part: Optional[List[Dataset]] = Field(
        default_factory=list,
        description="""A dataset that is associated with the study.""",
    )


class Publication(Document):
    """
    A published paper or written work.
    """

    pubmed_id: Optional[str] = Field(
        None, description="""Identifier for journal articles/abstracts in PubMed"""
    )
    doi: str = Field(description="""Digital Object Identifier (DOI)""")


class Dataset(BaseModel):
    """
    A logical grouping of data (in files) associated with a Study based on the process involved in creation of the files.
    """

    image: List[Image] = Field(description="""Images associated with the dataset""")
    file: List[FileRepresentation] = Field(
        description="""Files associated with the dataset"""
    )
    creation_method: list[Process] = Field(
        description="""Processes involved in the creation of the images and files in this dataset."""
    )


class ExternalReference(BaseModel):
    """
    An object outside the BIA that a user wants to refer to.
    """

    link: AnyUrl = Field(description="""A URL linking to the refered resource.""")
    description: Optional[str] = Field(
        None,
        description="""Brief description of the resource and how it relates to the document providing the reference.""",
    )


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

    sample_of: List[Biosample] = Field(
        description="""The biological matter that sampled to create the specimen."""
    )
    sample_preparation_description: Optional[str] = Field(
        None, description="""How the sample was prepared for imaging."""
    )
    signal_contrast_mechanism_description: Optional[str] = Field(
        None, description="""How is the signal is generated by this sample."""
    )
    growth_protocol_description: Optional[str] = Field(
        None,
        description="""How the specimen was grown, e.g. cell line cultures, crosses or plant growth.""",
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
    The biological entity that has undergone preparation (as a Sample) in order to be imaged.
    """

    organism_classification: List[Taxon] = Field(
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


class FileRepresentation(BaseModel):
    """
    The digital representation of a document.
    """

    file_name: str = Field(description="""The name of the file.""")
    format: str = Field(description="""File format or type.""")
    size_in_bytes: int = Field(description="""Disc size in bytes.""")
    uri: str = Field(description="""URI from which the file can be accessed.""")


class ImageRepresentation(FileRepresentation):
    """
    The manifestation of an image, represented in a particular image file format.
    """

    physical_dimension: Optional[str] = Field(
        None, description="""Size of the physical space captured by the image"""
    )
    digital_dimension: Optional[str] = Field(
        None, description="""Size in pixels or voxels of the image"""
    )
    image_viewer_setting: Optional[List[RenderedView]] = Field(
        None,
        description="""Settings of a particular view of an image, such as a specific timestamp of a timeseries, or camera placement in a 3D model.""",
    )


class AnnotationRepresation(FileRepresentation):
    """
    A file providing additional metadata or highlighting parts of an image.
    """

    source_image: ImageRepresentation = Field(
        description="""The original image this file is annotating."""
    )


class RenderedView(BaseModel):
    """
    A particular view of an image, such as as a specific timestamp of a time series, or a view direction of a 3D model.
    """

    z: Optional[str] = Field(
        None, description="""A z-value for the position of the image view"""
    )
    t: Optional[str] = Field(
        None, description="""A t-value for the timestamp of the image view"""
    )
    channel_information: Optional[List[Channel]] = Field(
        None,
        description="""Information about the channels involved in displaying this view of the image.""",
    )


class Channel(BaseModel):
    """
    An image channel.
    """

    colormap_start: float = Field(description="""Start value of colormap""")
    colormap_end: float = Field(description="""End value of colormap""")
    scale_factor: float = Field(None)
    label: Optional[str] = Field(
        None, description="""Label describing the channel for display."""
    )


# PostProcessing classes: Annotations, Image Correlations, and data analysis


class Process(BaseModel):
    """
    A process of either capturing, combining, or analysing images.
    """

    method_description: str = Field(
        description="""Description of processing method, e.g. light sheet fluorescence microscopy, class labels, segmentation masks, manual overlay"""
    )


class ImagingMethod(Process):
    """
    A process or method of capturing images.
    """

    fbbi_id: List[str] = Field(
        description="""Biological Imaging Methods Ontology id indicating the kind of imaging that was perfomed."""
    )
    method_description: str = Field(
        description="""A description of the imaging methods involved in creating the images in this dataset, e.g. light sheet fluorescence microscopy."""
    )
    pass


class Annotation(Process):
    """
    Information about the annotation process, such as methods used, or how much of a dataset was annotated.
    """

    source_dataset: List[Union[Dataset | AnyUrl]] = Field(
        description="""The datasets that were annotated."""
    )
    method_description: str = Field(
        description="""Description of annotation method, e.g. class labels, segmentation masks etc.."""
    )
    annotation_criteria: str = Field(
        description="""Rules used to generate annotations."""
    )
    annotation_coverage: str = Field(
        description="""Which images from the dataset were annotated, and what percentage of the data has been annotated from what is available."""
    )


class ImageCorrelation(Process):
    """
    Information about the process of correlating the positions of multiple images.
    """

    method_description: str = Field(
        description="""Method used for spatial and/or temporal alignment of images from different modalities (e.g. manual overlay, alignment algorithm etc)."""
    )
    fiducials_used: str = Field(
        description="""Features from correlated datasets used for colocalization."""
    )
    transformation_matrix: str = Field()


class ImageAnalysis(Process):
    """
    Information about data analysis methods.
    """

    method_description: str = Field(
        description="""The steps performed during image analysis."""
    )
    features_analysed: str = Field()


# Enums


class LicenseType(str, Enum):
    # No Copyright. You can copy, modify, distribute and perform the work, even for commercial purposes, all without asking permission.
    CC0 = "CC0"
    # You are free to: Share — copy and redistribute the material in any medium or format. Adapt — remix, transform, and build upon the material  for any purpose, even commercially. You must give appropriate credit, provide a link to the license, and indicate if changes were made.  You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
    CC_BY_40 = "CC_BY_4.0"


class AnnotationType(str, Enum):

    # tags that identify specific features, patterns or classes in images
    class_labels = "class_labels"
    # rectangles completely enclosing a structure of interest within an image
    bounding_boxes = "bounding_boxes"
    # number of objects, such as cells, found in an image
    counts = "counts"
    # additional analytical data extracted from the images. For example, the image point spread function,the signal to noise ratio, focus information…
    derived_annotations = "derived_annotations"
    # polygons and shapes that outline a region of interest in the image. These can be geometrical primitives, 2D polygons, 3D meshes…
    geometrical_annotations = "geometrical_annotations"
    # graphical representations of the morphology, connectivity, or spatial arrangement of biological structures in an image. Graphs, such as skeletons or connectivity diagrams, typically consist of nodes and edges, where nodes represent individual elements or regions and edges represent the connections or interactions between them
    graphs = "graphs"
    # X, Y, and Z coordinates of a point of interest in an image (for example an object's centroid  or landmarks).
    point_annotations = "point_annotations"
    # an image, the same size as the source image, with the value of each pixel representing some biological identity or background region
    segmentation_mask = "segmentation_mask"
    # annotations marking the movement or trajectory of objects within a sequence of bioimages
    tracks = "tracks"
    # rough imprecise annotations that are fast to generate. These annotations are used, for example,  to detect an object without providing accurate boundaries
    weak_annotations = "weak_annotations"
    # other types of annotations, please specify in the annotation overview section
    other = "other"


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
# Need to do this in order to auto-generate the class diagram
Study.model_rebuild()
