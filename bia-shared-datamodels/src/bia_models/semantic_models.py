from __future__ import annotations

from enum import Enum
from datetime import date
from typing import List, Optional, Union

from pydantic import BaseModel, Field, EmailStr, AnyUrl


#######################################################################################################
# Subgraph 1: Documents, contributors & their affiliations
#######################################################################################################


class PersonMixin(BaseModel):
    """
    Person information
    """

    orcid: Optional[str] = Field(
        None, description="""Open Researcher and Contributor ID."""
    )


class OrganisationMixin(BaseModel):
    """
    Organisation information
    """

    rorid: Optional[str] = Field(
        None, description="""Reasearch Organisation Registry ID."""
    )
    address: Optional[str] = Field(
        None, description="""Comma separated lines of the address."""
    )
    website: Optional[AnyUrl] = Field(
        default=None,
        description="""The website page with information about the Organisation.""",
    )


class Contributor(PersonMixin, OrganisationMixin):
    """
    A person or group that contributed to the creation of a Document.
    """

    display_name: str = Field(
        description="""Name as it should be displayed on the BioImage Archive."""
    )
    affiliation: List[Affiliation] = Field(
        default_factory=list,
        description="""The organisation(s) a contributor is afiliated with.""",
    )
    contact_email: Optional[EmailStr] = Field(
        default=None, description="""An email address to contact the Contributor."""
    )
    role: Optional[str] = Field(
        default=None, description="""The role of the contributor."""
    )


class Affiliation(OrganisationMixin):
    """
    An organsiation that a contributor is affiliated with.
    """

    display_name: str = Field(
        description="""Name as it should be displayed on the BioImage Archive."""
    )


class DocumentMixin(BaseModel):
    """
    A documentary resource or body of scientific work.
    """

    author: List[Contributor] = Field(description="""The creators of the document.""")
    title: str = Field(
        description="""The title of a scientific document. This will usually be displayed when search results including your data are shown."""
    )
    release_date: date = Field(description="""Date of first publication""")
    keyword: Optional[List[str]] = Field(
        default_factory=list,
        description="""Keywords or tags used to describe the subject of a document""",
    )
    acknowledgement: Optional[str] = Field(
        default_factory=list,
        description="""Any person or group that should be acknowledged with the document.""",
    )
    description: Optional[str] = Field(
        None, description="""Brief description of the scientific document."""
    )


#######################################################################################################
# Subgraph 2: Studies and links to external information (publications, grants etc)
#######################################################################################################


class Study(DocumentMixin):
    """
    A piece of scientific work that resulted in the creation of imaging data.
    """

    accession_id: str = Field(description="""Unique ID provided by BioStudies.""")
    license: LicenseType = Field(
        description="""The license under which the data associated with the study is made avaliable."""
    )
    see_also: Optional[List[ExternalReference]] = Field(
        default_factory=list,
        description="""Links to publications, github repositories, and other pages related to this Study.""",
    )
    related_publication: Optional[List[Publication]] = Field(
        default_factory=list,
        description="""The publications that the work involved in the study contributed to.""",
    )
    grant: Optional[List[Grant]] = Field(
        default_factory=list, description="""The grants that funded the study."""
    )
    funding_statement: Optional[str] = Field(
        default_factory=list, description="""Description of how the study was funded."""
    )
    experimental_imaging_component: Optional[List[ExperimentalImagingDataset]] = Field(
        default_factory=list,
        description="""A dataset of that is associated with the study.""",
    )
    annotation_component: Optional[List[ImageAnnotationDataset]] = Field(
        default_factory=list, description=""""""
    )
    attribute: dict = Field(
        description="""Freeform key-value pairs from user provided metadata (e.g. filelist data) and experimental fields."""
    )
    # Override optional description in DocumentMixin
    description: str = Field(
        None, description="""Brief description of the scientific document."""
    )


class Publication(DocumentMixin):
    """
    A published paper or written work.
    """

    pubmed_id: Optional[str] = Field(
        None, description="""Identifier for journal articles/abstracts in PubMed"""
    )
    doi: str = Field(description="""Digital Object Identifier (DOI)""")


class ExternalReference(BaseModel):
    """
    An object outside the BIA that a user wants to refer to.
    """

    link: AnyUrl = Field(description="""A URL linking to the refered resource.""")
    link_type: Optional[str] = Field(
        None,
        description="""Classifies the link by website domain and/or use-case, which is useful for display purposes and faceting search.""",
    )
    description: Optional[str] = Field(
        None,
        description="""Brief description of the resource and how it relates to the document providing the reference.""",
    )


class Grant(BaseModel):
    """ """

    id: Optional[str] = Field(
        None,
        description="""A unique identifier for the grant, such as an Open Funder Registry ID.""",
    )

    funder: Optional[List[FundingBody]] = Field(
        default_factory=list,
        description="""The name of the funding body providing support for the grant.""",
    )


class FundingBody(BaseModel):
    """ """

    display_name: str = Field(
        description="""Name as it should be displayed on the BioImage Archive."""
    )
    id: Optional[str] = Field(
        None,
        description="""A unique identifier for the Funder, such as an Open Funder Registry ID.""",
    )


class LicenseType(str, Enum):
    # No Copyright. You can copy, modify, distribute and perform the work, even for commercial purposes, all without asking permission.
    CC0 = "CC0"
    # You are free to: Share — copy and redistribute the material in any medium or format. Adapt — remix, transform, and build upon the material  for any purpose, even commercially. You must give appropriate credit, provide a link to the license, and indicate if changes were made.  You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
    CC_BY_40 = "CC_BY_4.0"


#######################################################################################################
# Subgraph 3: Dataset mixin and it's files. Method (of dataset creation/maniuplation) mixin.
#######################################################################################################


class DatasetMixin(BaseModel):
    """
    A logical grouping of data (in files) based on the process involved in it's creation.
    """

    file: List[FileReference] = Field(
        description="""Files associated with the dataset"""
    )
    file_reference_count: int = Field(
        description="""Number of files associated with the study."""
    )
    submitted_in_study: Study = Field(
        description="""The study the dataset was submitted in."""
    )


class FileReference(BaseModel):
    """
    Information about a file, provided in file list.
    """

    file_name: str = Field(description="""The name of the file.""")
    format: str = Field(description="""File format or type.""")
    size_in_bytes: int = Field(description="""Disc size in bytes.""")
    uri: str = Field(description="""URI from which the file can be accessed.""")
    attribute: dict = Field(
        description="""Freeform key-value pairs from user provided metadata (e.g. filelist data) and experimental fields."""
    )


class ProtocolMixin(BaseModel):
    """
    A protocol for either capturing, combining, or analysing images.
    """

    method_description: str = Field(
        description="""Description of steps involved in the process or method."""
    )


#######################################################################################################
# Subgraph 4: Abstract images & their representations
#######################################################################################################


class AbstractImageMixin(BaseModel):
    """
    The abstract notion of an image that can have many representions in different image formats.
    """

    representation: List[ImageRepresentation] = Field(
        description="""Representation(s) of the image in a specific image format."""
    )
    attribute: dict = Field(
        description="""Freeform key-value pairs from user provided metadata (e.g. filelist data) and experimental fields."""
    )


class ImageRepresentation(BaseModel):
    """
    The viewable or processable represention of an image in a particular image file format.
    This object was created from one or more file refences (usually one) provided by submitters to the BioImage Archive.
    """

    image_format: str = Field(description="""Image format of the combined files.""")
    file_uri: List[str] = Field(
        description="""URI(s) of the file(s) which together make up this image representation."""
    )
    total_size_in_bytes: int = Field(
        description="""Combined disc size in bytes of all the files."""
    )
    physical_size_x: Optional[float] = Field(
        None,
        description="""Size of the physical space (in meters) captured in the field of view of the image.""",
    )
    physical_size_y: Optional[float] = Field(
        None,
        description="""Size of the physical space (in meters) captured in the field of view of the image.""",
    )
    physical_size_z: Optional[float] = Field(
        None,
        description="""Size of the physical space (in meters) captured in the field of view of the image.""",
    )
    size_x: Optional[int] = Field(
        None,
        description="""Pixels or voxels dimension of the data array of the image.""",
    )
    size_y: Optional[int] = Field(
        None,
        description="""Pixels or voxels dimension of the data array of the image.""",
    )
    size_z: Optional[int] = Field(
        None,
        description="""Pixels or voxels dimension of the data array of the image.""",
    )
    size_c: Optional[int] = Field(
        None,
        description="""Number of channels of the image.""",
    )
    size_t: Optional[int] = Field(
        None,
        description="""Size of temporal dimension of the data array of the image).""",
    )
    image_viewer_setting: Optional[List[RenderedView]] = Field(
        None,
        description="""Settings of a particular view of an image, such as a specific timestamp of a timeseries, or camera placement in a 3D model.""",
    )
    original_file_reference: Optional[List[FileReference]] = Field(
        default_factory=list,
        description="""The user sumbitted file references from which this image representation was created. 
                    If this ImageRepresentation was created by conversion from another representation this will be empty.""",
    )
    attribute: dict = Field(
        description="""Freeform key-value pairs from user provided metadata (e.g. filelist data) and experimental fields."""
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


#######################################################################################################
# Subgraph 5: ImagingStudyComponents, Images, Acquisitions, Specimens, BioSample
#######################################################################################################


class ExperimentalImagingDataset(DatasetMixin):
    """
    A logical collection of images that were created by the same acquisition and preparation procols being applied to a biosample.
    """

    image: List[ExperimentallyCapturedImage] = Field(
        description="""Images associated with the dataset."""
    )
    acquisition_method: list[ImageAcquisition] = Field(
        description="""Processes involved in the creation of the images and files in this dataset."""
    )
    specimen_preparation_method: list[SpecimenPrepartionProtocol] = Field(
        description="""Processes involved in the creation of the samples that were then imaged."""
    )
    biological_entity: list[BioSample] = Field(
        description="""The biological entity that was imaged."""
    )
    analysis_method: Optional[list[ImageAnalysisMethod]] = Field(
        description="""Data analysis processes performed on the images."""
    )
    correlation_method: Optional[list[ImageCorrelationMethod]] = Field(
        description="""Processes performed to correlate image data."""
    )
    example_image_uri: list[str] = Field(
        description="A viewable image that is typical of the dataset."
    )
    image_count: int = Field(
        description="""Number of images associated with the dataset."""
    )


class ExperimentallyCapturedImage(AbstractImageMixin):
    """
    The abstract result of subject being captured by an image acquisition event. This can have many representions in different image formats.
    """

    acquisition_process: List[ImageAcquisition] = Field(
        description="""The processes involved in the creation of the image."""
    )
    subject: Specimen = Field(
        description="""The specimen that was prepared for and captured in the field of view of the image."""
    )
    submission_dataset: ExperimentalImagingDataset = Field(
        description="""The dataset in which image was first submitted to the BIA."""
    )


class ImageAcquisition(BaseModel):
    """
    The process with which an image is captured.
    """

    imaging_instrument_description: str = Field(
        description="""Names, types, or description of how the instruments used to create the image."""
    )
    image_acquisition_parameters: str = Field(
        description="""Parameters relevant to how the image was taken, such as instrument settings."""
    )
    fbbi_id: List[str] = Field(
        description="""Biological Imaging Methods Ontology id indicating the kind of imaging that was perfomed."""
    )


class SpecimenPrepartionProtocol(BaseModel):
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


class Specimen(BaseModel):
    """
    The subject of an image acquisition, and the result of a BioSample being prepared to be imaged.
    """

    sample_of: List[BioSample] = Field(
        description="""The biological matter that sampled to create the specimen."""
    )
    preparation_method: List[SpecimenPrepartionProtocol] = Field(
        description="""How the biosample was prepared for imaging."""
    )


class BioSample(BaseModel):
    """
    The biological entity that has undergone preparation (as a Sample) in order to be imaged.
    """

    organism_classification: List[Taxon] = Field(
        description="""The classification of th ebiological matter."""
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


class ImageAnalysisMethod(ProtocolMixin):
    """
    Information about image analysis methods.
    """

    features_analysed: str = Field(description="""""")


class ImageCorrelationMethod(ProtocolMixin):
    """
    Information about the process of correlating the positions of multiple images.
    """

    fiducials_used: str = Field(
        description="""Features from correlated datasets used for colocalization."""
    )
    transformation_matrix: str = Field(description="""Correlation transforms.""")


#######################################################################################################
# Subgraph 6: Annotation dataset, annotations etc.
#######################################################################################################


class ImageAnnotationDataset(DatasetMixin):
    """
    Information about the annotation process, such as methods used, or how much of a dataset was annotated.
    """

    annotation_method: List[AnnotationMethod] = Field(
        description="""The process(es) that were performed to create the annotated data."""
    )
    annotation_file: List[AnnotationFileReference] = Field(
        description="""Annotation files associated with the dataset."""
    )
    image: List[DerivedImage] = Field(
        description="""Images associated with the dataset."""
    )
    example_image_uri: list[str] = Field(
        description="A viewable image that is typical of the dataset."
    )
    image_count: int = Field(
        description="""Number of images associated with the dataset."""
    )


class AnnotationMethod(ProtocolMixin):
    """
    Information about the annotation process, such as methods used, or how much of a dataset was annotated.
    """

    source_dataset: List[Union[ExperimentalImagingDataset | AnyUrl]] = Field(
        description="""The datasets that were annotated."""
    )
    annotation_criteria: str = Field(
        description="""Rules used to generate annotations."""
    )
    annotation_coverage: str = Field(
        description="""Which images from the dataset were annotated, and what percentage of the data has been annotated from what is available."""
    )
    method_type: AnnotationType = Field(
        description="""Classification of the kind of annotation that was performed."""
    )


class AnnotationMixin(BaseModel):
    """
    Information providing additional metadata or highlighting parts of an image.
    """

    source_image: List[ImageRepresentation] = Field(
        description="""The original image(s) this file is annotating."""
    )
    transformation_description: str = Field(
        description="""Any transformations required to link annotations to the image."""
    )
    spatial_information: str = Field(
        description="""Spatial information for non-pixel annotations."""
    )
    creation_process: AnnotationMethod = Field(
        description="""The process that was followed to create the annotation."""
    )


class AnnotationFileReference(FileReference, AnnotationMixin):
    """
    An file that is an annotation of an image.
    """

    pass


class DerivedImage(AnnotationMixin, AbstractImageMixin):
    """
    An image that is an annotation of another image.
    """

    submission_dataset: ImageAnnotationDataset = Field(
        description="""The dataset in which image was first submitted to the BIA."""
    )


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


#######################################################################################################
# Other (unsure where to classify for now)
#######################################################################################################


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
# Need to do this in order to auto-generate the class diagram
Contributor.model_rebuild()
DocumentMixin.model_rebuild()
Study.model_rebuild()
DatasetMixin.model_rebuild()
ImageAnnotationDataset.model_rebuild()
ExperimentalImagingDataset.model_rebuild()
