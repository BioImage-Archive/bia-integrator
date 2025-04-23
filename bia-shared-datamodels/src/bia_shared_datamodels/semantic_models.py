from __future__ import annotations

from enum import Enum
from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, EmailStr, AnyUrl, ConfigDict


#######################################################################################################
# Generic Classes
#######################################################################################################


class ConfiguredBaseModel(BaseModel):
    # Throw error if you try to validate/create model from a dictionary with keys that aren't a field in the model
    model_config = ConfigDict(extra="forbid")


class AttributeProvenance(str, Enum):
    submittor = "submittor"

    bia_ingest = "bia_ingest"

    bia_conversion = "bia_conversion"

    bia_curation = "bia_curation"


class Attribute(ConfiguredBaseModel):
    provenance: AttributeProvenance = Field(
        description="The category of the source of the annotaton"
    )
    name: str = Field(
        description="A descriptive name or identifier for the annotation."
    )
    value: dict = Field(
        description="The value of an annotation, which is a stored in a freeform dicitionary"
    )


class AttributeMixin(BaseModel):
    """
    Mixin for just the attribute field
    """

    attribute: Optional[list[Attribute]] = Field(
        default_factory=list,
        description="""Freeform key-value pairs from user provided metadata (e.g. filelist data) and experimental fields.""",
    )


#######################################################################################################
# Subgraph 1: Studies and links to external information (publications, grants etc)
#######################################################################################################


class Study(ConfiguredBaseModel, AttributeMixin):
    """
    A piece of scientific work that resulted in the creation of imaging data.
    """

    accession_id: str = Field(description="""Unique ID provided by BioStudies.""")
    licence: Licence = Field(
        description="""The license under which the data associated with the study is made avaliable."""
    )
    author: List[Contributor] = Field(description="""The creators of the document.""")
    title: str = Field(
        description="""The title of a study. This will usually be displayed when search results including your data are shown."""
    )
    release_date: date = Field(description="""Date of first publication""")
    description: str = Field(description="""Brief description of the study.""")
    keyword: Optional[List[str]] = Field(
        default_factory=list,
        description="""Keywords or tags used to describe the subject or context of the study.""",
    )
    acknowledgement: Optional[str] = Field(
        None,
        description="""Any person or group that should be acknowledged outside of the authors/main contributors to the study.""",
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
        None, description="""Description of how the study was funded."""
    )


class Publication(ConfiguredBaseModel):
    """
    A published paper or written work.
    """

    authors_name: str = Field(
        description="""The list of names of the authors as displayed in the publication."""
    )
    title: str = Field(description="""The title of the publication.""")
    publication_year: int = Field(description="""Year the article was published""")
    pubmed_id: Optional[str] = Field(
        None, description="""Identifier for journal articles/abstracts in PubMed"""
    )
    doi: Optional[str] = Field(None, description="""Digital Object Identifier (DOI)""")


class ExternalReference(ConfiguredBaseModel):
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


class Grant(ConfiguredBaseModel):
    """ """

    id: Optional[str] = Field(
        None,
        description="""A unique identifier for the grant, such as an Open Funder Registry ID.""",
    )

    funder: Optional[List[FundingBody]] = Field(
        default_factory=list,
        description="""The name of the funding body providing support for the grant.""",
    )


class FundingBody(ConfiguredBaseModel):
    """ """

    display_name: str = Field(
        description="""Name as it should be displayed on the BioImage Archive."""
    )
    id: Optional[str] = Field(
        None,
        description="""A unique identifier for the Funder, such as an Open Funder Registry ID.""",
    )


class Licence(str, Enum):
    # No Copyright. You can copy, modify, distribute and perform the work, even for commercial purposes, all without asking permission.
    CC0 = "https://creativecommons.org/publicdomain/zero/1.0/"
    # You are free to: Share — copy and redistribute the material in any medium or format. Adapt — remix, transform, and build upon the material  for any purpose, even commercially. You must give appropriate credit, provide a link to the license, and indicate if changes were made.  You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
    CC_BY_40 = "https://creativecommons.org/licenses/by/4.0/"
    CC_BY_30 = "https://creativecommons.org/licenses/by/3.0/"
    CC_BY_25 = "https://creativecommons.org/licenses/by/2.5/"
    CC_BY_20 = "https://creativecommons.org/licenses/by/2.0/"
    CC_BY_10 = "https://creativecommons.org/licenses/by/1.0/"

    CC_BY_SA_40 = "https://creativecommons.org/licenses/by-sa/4.0/"
    CC_BY_SA_30 = "https://creativecommons.org/licenses/by-sa/3.0/"
    CC_BY_SA_25 = "https://creativecommons.org/licenses/by-sa/2.5/"
    CC_BY_SA_20 = "https://creativecommons.org/licenses/by-sa/2.0/"
    CC_BY_SA_10 = "https://creativecommons.org/licenses/by-sa/1.0/"

    CC_BY_SA_21_JP = "https://creativecommons.org/licenses/by-sa/2.1/jp/"

    CC_BY_NC_40 = "https://creativecommons.org/licenses/by-nc/4.0/"
    CC_BY_NC_30 = "https://creativecommons.org/licenses/by-nc/3.0/"
    CC_BY_NC_25 = "https://creativecommons.org/licenses/by-nc/2.5/"
    CC_BY_NC_20 = "https://creativecommons.org/licenses/by-nc/2.0/"
    CC_BY_NC_10 = "https://creativecommons.org/licenses/by-nc/1.0/"

    CC_BY_NC_SA_40 = "https://creativecommons.org/licenses/by-nc-sa/4.0/"
    CC_BY_NC_SA_30 = "https://creativecommons.org/licenses/by-nc-sa/3.0/"
    CC_BY_NC_SA_25 = "https://creativecommons.org/licenses/by-nc-sa/2.5/"
    CC_BY_NC_SA_20 = "https://creativecommons.org/licenses/by-nc-sa/2.0/"
    CC_BY_NC_SA_10 = "https://creativecommons.org/licenses/by-nc-sa/1.0/"

    # Note ND is 'No derivatives'

    CC_BY_NC_ND_40 = "https://creativecommons.org/licenses/by-nc-nd/4.0/"

class ImageRepresentationUseType(str, Enum):
    """Enumerate use types of ImageRepresentations"""

    # Original format uploaded with the study
    UPLOADED_BY_SUBMITTER = "UPLOADED_BY_SUBMITTER"
    # Usually used as representative image for study
    STATIC_DISPLAY = "STATIC_DISPLAY"
    # To be used as thumbnail
    THUMBNAIL = "THUMBNAIL"
    # Allows remote interactive exploration - usually ome zarr format
    INTERACTIVE_DISPLAY = "INTERACTIVE_DISPLAY"


#######################################################################################################
# Subgraph 2: Contributors & their affiliations
#######################################################################################################


class PersonMixin(ConfiguredBaseModel):
    """
    Person information
    """

    orcid: Optional[str] = Field(
        None, description="""Open Researcher and Contributor ID."""
    )


class OrganisationMixin(ConfiguredBaseModel):
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
        None,
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
        description="""The organisation(s) a contributor is afiliated with.""",
    )
    contact_email: Optional[EmailStr] = Field(
        None, description="""An email address to contact the Contributor."""
    )
    role: Optional[str] = Field(None, description="""The role of the contributor.""")


class Affiliation(OrganisationMixin):
    """
    An organsiation that a contributor is affiliated with.
    """

    display_name: str = Field(
        description="""Name as it should be displayed on the BioImage Archive."""
    )


#######################################################################################################
# Subgraph 3: Dataset, File References
#######################################################################################################


class Dataset(ConfiguredBaseModel, AttributeMixin):
    """
    A logical collection of images that were created by the same acquisition and preparation procols being applied to a biosample.
    """

    title: str = Field(description="""The title of a dataset.""")
    description: Optional[str] = Field(
        None, description="""Brief description of the dataset."""
    )
    analysis_method: Optional[list[ImageAnalysisMethod]] = Field(
        default_factory=list,
        description="""Data analysis processes performed on the images.""",
    )
    correlation_method: Optional[list[ImageCorrelationMethod]] = Field(
        default_factory=list,
        description="""Processes performed to correlate image data.""",
    )
    example_image_uri: list[str] = Field(
        description="A viewable image that is typical of the dataset."
    )


class FileReference(ConfiguredBaseModel, AttributeMixin):
    """
    Information about a file, provided in file list.
    """

    file_path: str = Field(description="""The path (including the name) of the file.""")
    # TODO: Clarify if this should be biostudies 'type' or derived from file extension
    format: str = Field(description="""File format or type.""")
    size_in_bytes: int = Field(description="""Disc size in bytes.""")
    uri: str = Field(description="""URI from which the file can be accessed.""")


#######################################################################################################
# Subgraph 4: Images & representations
#######################################################################################################


class Image(ConfiguredBaseModel, AttributeMixin):
    """
    The abstract notion of an image that can have many representions in different image formats. A BIA image has been created from a unique set of File References.
    """

    label: Optional[str] = Field(
        None,
        description="""Optional human readable label describing or titling the image.""",
    )


class ImageRepresentation(ConfiguredBaseModel, AttributeMixin):
    """
    The viewable or processable represention of an image in a particular image file format.
    This object was created from one or more file refences (usually one) provided by submitters to the BioImage Archive.
    """

    image_format: str = Field(description="""Image format of the combined files.""")
    use_type: ImageRepresentationUseType = Field(
        description="""The use case of this particular image representation i.e. thumbnail, interactive display etc."""
    )
    file_uri: List[str] = Field(
        description="""URI(s) of the file(s) which together make up this image representation."""
    )
    total_size_in_bytes: int = Field(
        description="""Combined disc size in bytes of all the files."""
    )
    voxel_physical_size_x: Optional[float] = Field(
        None,
        description="""Size of the physical space (in meters) captured by a single pixel or voxel of the image.""",
    )
    voxel_physical_size_y: Optional[float] = Field(
        None,
        description="""Size of the physical space (in meters) captured by a single pixel or voxel of the image.""",
    )
    voxel_physical_size_z: Optional[float] = Field(
        None,
        description="""Size of the physical space (in meters) captured by a single pixel or voxel of the image.""",
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
        description="""Number of timesteps in the temporal dimension of the data array of the image.""",
    )
    image_viewer_setting: Optional[List[RenderedView]] = Field(
        default_factory=list,
        description="""Settings of a particular view of an image, such as a specific timestamp of a timeseries, or camera placement in a 3D model.""",
    )


class RenderedView(ConfiguredBaseModel, AttributeMixin):
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
        default_factory=list,
        description="""Information about the channels involved in displaying this view of the image.""",
    )


class Channel(ConfiguredBaseModel, AttributeMixin):
    """
    An image channel.
    """

    colormap_start: float = Field(description="""Start value of colormap""")
    colormap_end: float = Field(description="""End value of colormap""")
    scale_factor: Optional[float] = Field(None)
    label: Optional[str] = Field(
        None, description="""Label describing the channel for display."""
    )


class AnnotationData(ConfiguredBaseModel, AttributeMixin):
    """
    Annotation data that is not captured in an image/viewable form, such as a table of labels for many different images.
    """

    pass


#######################################################################################################
# Subgraph 5: Process & Protocols
#######################################################################################################


class CreationProcess(ConfiguredBaseModel, AttributeMixin):
    """
    The combination of some protocol that was followed with particular inputs that resulted in the creation of an image.
    """

    pass


class Protocol(ConfiguredBaseModel, AttributeMixin):
    """
    The description of a sequence of actions that were perfomed.
    """

    title: str = Field(description="""The title of a protocol.""")
    protocol_description: str = Field(
        description="""Description of actions involved in the process."""
    )


class ImageAcquisitionProtocol(Protocol):
    """
    The process with which an image is captured.
    """

    imaging_instrument_description: str = Field(
        description="""Names, types, or description of how the instruments used to create the image."""
    )
    fbbi_id: Optional[List[str]] = Field(
        default_factory=list,
        description="""Biological Imaging Methods Ontology id indicating the kind of imaging that was perfomed.""",
    )
    imaging_method_name: Optional[List[str]] = Field(
        default_factory=list,
        description="""Name of the kind of imaging method that was performed.""",
    )


class SpecimenImagingPreparationProtocol(Protocol):
    """
    The process to prepare biological entity for imaging.
    """

    signal_channel_information: Optional[List[SignalChannelInformation]] = Field(
        default_factory=list,
        description="""Information about how channels in the image relate to image signal generation.""",
    )


class SignalChannelInformation(ConfiguredBaseModel, AttributeMixin):
    """
    Information about how signals were generated, staining compounds and their targets.
    """

    signal_contrast_mechanism_description: Optional[str] = Field(
        None, description="""How is the signal is generated by this sample."""
    )
    channel_content_description: Optional[str] = Field(
        None,
        description="""What staining was used in preparation of the specimen (e.g. IEM, DAB).""",
    )
    channel_biological_entity: Optional[str] = Field(
        None, description="""What molecule is stained."""
    )
    channel_label: Optional[str] = Field(
        default=None,
        description="""Label in the image for the channel. Often this is some integer e.g. 1 or Channel 1""",
    )


class AnnotationMethod(Protocol):
    """
    Information about the annotation process, such as methods used, or how much of a dataset was annotated.
    """

    annotation_criteria: Optional[str] = Field(
        None, description="""Rules used to generate annotations."""
    )
    annotation_coverage: Optional[str] = Field(
        None,
        description="""Which images from the dataset were annotated, and what percentage of the data has been annotated from what is available.""",
    )
    transformation_description: Optional[str] = Field(
        None,
        description="""Any transformations required to link annotations to the image.""",
    )
    spatial_information: Optional[str] = Field(
        None, description="""Spatial information for non-pixel annotations."""
    )
    method_type: List[AnnotationMethodType] = Field(
        description="""Classification of the kind of annotation that was performed."""
    )
    annotation_source_indicator: Optional[AnnotationSourceIndicator] = Field(
        None,
        description="""How the file(s) containing annotation data can be linked to the original images that were annotated.""",
    )


class ImageAnalysisMethod(Protocol):
    """
    Information about image analysis methods.
    """

    features_analysed: Optional[str] = Field(
        None,
        description="""Which features of the image were central to the analysis method.""",
    )


class ImageCorrelationMethod(Protocol):
    """
    Information about the process of correlating the positions of multiple images.
    """

    fiducials_used: Optional[str] = Field(
        None,
        description="""Features from correlated datasets used for colocalization.""",
    )
    transformation_matrix: Optional[str] = Field(
        None, description="""Correlation transforms."""
    )


class AnnotationMethodType(str, Enum):
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


class AnnotationSourceIndicator(str, Enum):
    # A metadata file is provided linking every annotation to their source file(s)
    metadata_file = "metadata_file"
    # files are named exactly the same, but exist in different directories
    file_name_exact_match = "file_name_exact_match"
    # files follow a similar naming pattern e.g. img_1_raw and img_1_annotation
    file_name_pattern = "file_name_pattern"
    # Annotation and their source are grouped together by a parent directory
    file_path = "file_path"
    # Some other method is used to connect the files, please specify in the annotation method description.
    other = "other"


#######################################################################################################
# Subgraph 6: Specimen, Biosample etc
#######################################################################################################


class Specimen(ConfiguredBaseModel, AttributeMixin):
    """
    The subject of an image acquisition, and the result of a BioSample being prepared to be imaged.
    """

    pass


class BioSample(ConfiguredBaseModel, AttributeMixin):
    """
    The biological entity that has undergone preparation (as a Sample) in order to be imaged.
    """

    title: str = Field(description="""The title of a bio-sample.""")
    organism_classification: List[Taxon] = Field(
        description="""The classification of th ebiological matter."""
    )
    biological_entity_description: str = Field(
        description="""A short description of the biological entity."""
    )
    experimental_variable_description: Optional[List[str]] = Field(
        default_factory=list,
        description="""What is intentionally varied (e.g. time) between multiple entries in this study component""",
    )
    extrinsic_variable_description: Optional[List[str]] = Field(
        default_factory=list, description="External treatment (e.g. reagent)."
    )
    intrinsic_variable_description: Optional[List[str]] = Field(
        default_factory=list, description="Intrinsic (e.g. genetic) alteration."
    )


class Taxon(ConfiguredBaseModel, AttributeMixin):
    """
    The classification of a biological entity.
    """

    common_name: Optional[str] = Field(
        None,
        description="""Name used to refer to the species that can vary by locallity.""",
    )
    scientific_name: Optional[str] = Field(
        None,
        description="""unique name used by the scientific community to identify species.""",
    )
    ncbi_id: Optional[str] = Field(
        None,
        description="""unique name used by the scientific community to identify species.""",
    )


#######################################################################################################
# Other
#######################################################################################################


class SupportingFile(ConfiguredBaseModel, AttributeMixin):
    """
    A logical grouping of data (in files) based on the process involved in it's creation.
    """

    pass


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
# Need to do this in order to auto-generate the class diagram
Contributor.model_rebuild()
Study.model_rebuild()
Dataset.model_rebuild()
BioSample.model_rebuild()
SpecimenImagingPreparationProtocol.model_rebuild()
AnnotationMethod.model_rebuild()
ImageRepresentation.model_rebuild()
FileReference.model_rebuild()
