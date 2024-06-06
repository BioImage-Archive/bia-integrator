```mermaid
classDiagram

    class Biosample {
        organism_classification: list[Taxon]
        description: str
        experimental_variable_description: list[str] | None
        extrinsic_variable_description: list[str] | None
        intrinsic_variable_description: list[str] | None
    }

    class Organisation {
        rorid: str | None = None
        address: str | None = None
    }

    class Dataset {
        image: list[Image]
        file: list[FileRepresentation]
        creation_method: list[Process]
    }

    class Image {
        represenatation: list[ImageRepresentation]
        acquisition_process: list[ImageAcquisition]
    }

    class RenderedView {
        z: str | None = None
        t: str | None = None
        channel_information: list[Channel] | None = None
    }

    class ImageRepresentation {
        physical_dimension: str | None = None
        digital_dimension: str | None = None
        image_viewer_setting: list[RenderedView] | None = None
    }

    class FileRepresentation {
        file_name: str
        format: str
        size_in_bytes: int
        uri: str
    }

    class Channel {
        colormap_start: float
        colormap_end: float
        scale_factor: float = None
        label: str | None = None
    }

    class Person {
        orcid: str | None = None
    }

    class ImageCaptureProcess {
        fbbi_id: list[str]
    }

    class ImageAcquisition {
        subject: list[Specimen]
        imaging_instrument_description: str
        image_acquistion_parameters: str
    }

    class Publication {
        pubmed_id: str | None = None
        doi: str
    }

    class ImageCorrelation {
        fiducials_used: str
    }

    class Process {
        method_description: str
    }

    class Agent {
        display_name: str
        contact_email: EmailStr
        member_of: list[Organisation] | None = list
    }

    class AnalysedData {
    }

    class Document {
        author: list[Agent]
        title: str
        release_date: date
        keywords: list[str] | None = list
        acknowledgement: list[Agent] | None = list
        description: str | None = None
    }

    class ExternalReference {
        link: Url
        description: str | None = None
    }

    class Study {
        accession_id: str
        file_reference_count: int
        image_count: int
        license: LicenseType
        see_also: list[ExternalReference] | None = list
        contributed_publication: list[Publication] | None
        funding: list[Grant] | None = list
        part: list[Dataset] | None = list
    }

    class Grant {
        id: str | None = None
        funder: list[Agent] = list
    }

    class Annotation {
        source_dataset: Dataset | Url
        annotation_criteria: str
        annotation_coverage: str
    }

    class AnnotationRepresation {
        source_image: ImageRepresentation
    }

    class Specimen {
        sample_of: list[Biosample]
        sample_preparation_description: str | None = None
        signal_contrast_mechanism_description: str | None = None
        growth_protocol_description: str | None = None
        channel_content_description: str | None = None
        channel_biological_entity: str | None = None
    }

    class LicenseType {
        <<Enumeration>>
        CC0: str = 'CC0'
        CC_BY_40: str = 'CC_BY_4.0'
    }

    class Taxon {
        common_name: str | None = None
        scientific_name: str | None = None
        ncbi_id: str | None = None
    }

    Agent ..> EmailStr
    Agent ..> Organisation
    Grant ..> Agent
    Document ..> Agent
    Study ..> Publication
    Study ..> Grant
    Study ..> Dataset
    Study ..> LicenseType
    Study ..> ExternalReference
    Dataset ..> FileRepresentation
    Dataset ..> Image
    Dataset ..> Process
    Image ..> ImageRepresentation
    Image ..> ImageAcquisition
    ImageAcquisition ..> Specimen
    Specimen ..> Biosample
    Biosample ..> Taxon
    ImageRepresentation ..> RenderedView
    AnnotationRepresation ..> ImageRepresentation
    RenderedView ..> Channel
    Annotation ..> Dataset

    Agent <|-- Organisation
    Agent <|-- Person
    Document <|-- Study
    Document <|-- Publication
    FileRepresentation <|-- ImageRepresentation
    FileRepresentation <|-- AnnotationRepresation
    Process <|-- AnalysedData
    Process <|-- ImageCaptureProcess
    Process <|-- Annotation
    Process <|-- ImageCorrelation

```