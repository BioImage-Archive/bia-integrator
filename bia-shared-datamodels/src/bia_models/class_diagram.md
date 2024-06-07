```mermaid
classDiagram

    class Image {
        represenatation: list[ImageRepresentation]
        acquisition_process: list[ImageAcquisition]
    }

    class Study {
        accession_id: str
        file_reference_count: int
        image_count: int
        license: LicenseType
        see_also: list[ExternalReference] | None = list
        related_publication: list[Publication] | None
        grant: list[Grant] | None = list
        funding_statement: str | None = list
        part: list[Dataset] | None = list
    }

    class ExternalReference {
        link: Url
        description: str | None = None
    }

    class ImageAcquisition {
        subject: list[Specimen]
        imaging_instrument_description: str
        image_acquistion_parameters: str
    }

    class Channel {
        colormap_start: float
        colormap_end: float
        scale_factor: float = None
        label: str | None = None
    }

    class Process {
        method_description: str
    }

    class Agent {
        display_name: str
        contact_email: EmailStr
        affiliation: list[Organisation] | None = list
        website: Url | None = None
    }

    class AnnotationType {
        <<Enumeration>>
        class_labels: str = 'class_labels'
        bounding_boxes: str = 'bounding_boxes'
        counts: str = 'counts'
        derived_annotations: str = 'derived_annotations'
        geometrical_annotations: str = 'geometrical_annotations'
        graphs: str = 'graphs'
        point_annotations: str = 'point_annotations'
        segmentation_mask: str = 'segmentation_mask'
        tracks: str = 'tracks'
        weak_annotations: str = 'weak_annotations'
        other: str = 'other'
    }

    class RenderedView {
        z: str | None = None
        t: str | None = None
        channel_information: list[Channel] | None = None
    }

    class Taxon {
        common_name: str | None = None
        scientific_name: str | None = None
        ncbi_id: str | None = None
    }

    class Person {
        orcid: str | None = None
    }

    class FileRepresentation {
        file_name: str
        format: str
        size_in_bytes: int
        uri: str
    }

    class Document {
        author: list[Agent]
        title: str
        release_date: date
        keyword: list[str] | None = list
        acknowledgement: list[Agent] | None = list
        description: str | None = None
    }

    class LicenseType {
        <<Enumeration>>
        CC0: str = 'CC0'
        CC_BY_40: str = 'CC_BY_4.0'
    }

    class Specimen {
        sample_of: list[Biosample]
        sample_preparation_description: str | None = None
        signal_contrast_mechanism_description: str | None = None
        growth_protocol_description: str | None = None
        channel_content_description: str | None = None
        channel_biological_entity: str | None = None
    }

    class Biosample {
        organism_classification: list[Taxon]
        description: str
        experimental_variable_description: list[str] | None
        extrinsic_variable_description: list[str] | None
        intrinsic_variable_description: list[str] | None
    }

    class Annotation {
        source_dataset: list[Dataset | Url]
        annotation_criteria: str
        annotation_coverage: str
    }

    class ImagingMethod {
        fbbi_id: list[str]
    }

    class ImageAnalysis {
        method_description: str = 'The steps performed during image analysis.'
        features_analysed: str
    }

    class Dataset {
        image: list[Image]
        file: list[FileRepresentation]
        creation_method: list[Process]
    }

    class Organisation {
        rorid: str | None = None
        address: str | None = None
    }

    class Grant {
        id: str | None = None
        funder: list[Agent] = list
    }

    class Publication {
        pubmed_id: str | None = None
        doi: str
    }

    class AnnotationRepresation {
        source_image: ImageRepresentation
    }

    class ImageRepresentation {
        physical_dimension: str | None = None
        digital_dimension: str | None = None
        image_viewer_setting: list[RenderedView] | None = None
    }

    class ImageCorrelation {
        fiducials_used: str
        transformation_matrix: str
    }

    Agent ..> Url
    Agent ..> EmailStr
    Agent ..> Organisation
    Grant ..> Agent
    Document ..> Agent
    Study ..> ExternalReference
    Study ..> Dataset
    Study ..> Grant
    Study ..> Publication
    Study ..> LicenseType
    Dataset ..> Image
    Dataset ..> FileRepresentation
    Dataset ..> Process
    ExternalReference ..> Url
    Image ..> ImageRepresentation
    Image ..> ImageAcquisition
    ImageAcquisition ..> Specimen
    Specimen ..> Biosample
    Biosample ..> Taxon
    ImageRepresentation ..> RenderedView
    AnnotationRepresation ..> ImageRepresentation
    RenderedView ..> Channel
    Annotation ..> Dataset
    Annotation ..> Url

    Agent <|-- Person
    Agent <|-- Organisation
    Document <|-- Publication
    Document <|-- Study
    FileRepresentation <|-- AnnotationRepresation
    FileRepresentation <|-- ImageRepresentation
    Process <|-- ImageAnalysis
    Process <|-- ImageCorrelation
    Process <|-- Annotation
    Process <|-- ImagingMethod

```