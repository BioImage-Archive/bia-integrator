from pydantic import BaseModel, Field, ConfigDict, BeforeValidator
from typing import Annotated


def string_to_list(value):
    if isinstance(value, str):
        return [value]
    return value


class ClosedBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SpecimenProposal(ClosedBaseModel):
    title: str = Field()
    biosample_title: str = Field()
    specimen_imaging_preparation_protocol_title: str = Field()


class Taxon(ClosedBaseModel):
    common_name: str = Field()
    scientific_name: str = Field()
    ncbi_id: str | None = Field(None)


class BioSampleProposal(ClosedBaseModel):
    title: str = Field()
    biological_entity_description: str = Field()
    organism_classification: list[Taxon] = Field()
    growth_protocol_title: Annotated[list[str], BeforeValidator(string_to_list)] = (
        Field(default_factory=list)
    )


class BioSampleReference(ClosedBaseModel):
    bio_sample_title: Annotated[list[str], BeforeValidator(string_to_list)] = Field(
        default_factory=list
    )


class SpecimenImagingPreparationProtocolProposal(ClosedBaseModel):
    title: str = Field()
    protocol_description: str = Field()


class SpecimenImagingPreparationProtocolReference(ClosedBaseModel):
    specimen_imaging_preparation_protocol_title: Annotated[
        list[str], BeforeValidator(string_to_list)
    ] = Field(default_factory=list)


class ImageAcquisitionProtocolProposal(ClosedBaseModel):
    title: str = Field()
    protocol_description: str = Field()
    imaging_instrument_description: str = Field()
    fbbi_id: list[str] = Field()
    imaging_method_name: list[str] = Field()


class ImageAcquisitionProtocolReference(ClosedBaseModel):
    image_acquisition_protocol_title: Annotated[
        list[str], BeforeValidator(string_to_list)
    ] = Field(default_factory=list)


class AnnotationMethodProposal(ClosedBaseModel):
    title: str = Field()
    protocol_description: str = Field()
    method_type: list[str] = Field()


class AnnotationMethodReference(ClosedBaseModel):
    annotation_method_title: Annotated[list[str], BeforeValidator(string_to_list)] = (
        Field(default_factory=list)
    )


class ProtocolProposal(ClosedBaseModel):
    title: str = Field()
    protocol_description: str = Field()


class ProtocolReference(ClosedBaseModel):
    protocol_title: Annotated[list[str], BeforeValidator(string_to_list)] = Field(
        default_factory=list
    )


class ImageAnalysisMethodProposal(ClosedBaseModel):
    title: str = Field()
    protocol_description: str = Field()
    features_analysed: str | None = Field(None)


class ImageAnalysisMethodReference(ClosedBaseModel):
    image_analysis_method_title: Annotated[
        list[str], BeforeValidator(string_to_list)
    ] = Field(default_factory=list)


class ImageCorrelationMethodProposal(ClosedBaseModel):
    title: str = Field()
    protocol_description: str = Field()
    fiducials_used: str | None = Field(None)
    transformation_matrix: str | None = Field(None)


class ImageCorrelationMethodReference(ClosedBaseModel):
    image_correlation_method_title: Annotated[
        list[str], BeforeValidator(string_to_list)
    ] = Field(default_factory=list)


class RembiByType(ClosedBaseModel):
    BioSample: list[BioSampleProposal] = Field(default_factory=list)
    SpecimenImagingPreparationProtocol: list[
        SpecimenImagingPreparationProtocolProposal
    ] = Field(default_factory=list)
    Specimen: list[SpecimenProposal] = Field(default_factory=list)
    ImageAcquisitionProtocol: list[ImageAcquisitionProtocolProposal] = Field(
        default_factory=list
    )
    AnnotationMethod: list[AnnotationMethodProposal] = Field(default_factory=list)
    Protocol: list[ProtocolProposal] = Field(default_factory=list)


class DatasetRembiByType(ClosedBaseModel):
    ImageAnalysisMethod: list[ImageAnalysisMethodProposal] = Field(default_factory=list)
    ImageCorrelationMethod: list[ImageCorrelationMethodProposal] = Field(
        default_factory=list
    )


class FileReferenceMixin(BaseModel):
    file_pattern: str | None = Field(None)


class ResultData(ClosedBaseModel, FileReferenceMixin):
    label: str | None = Field(None)
    label_prefix: str | None = Field(None)
    protocol_title: Annotated[list[str], BeforeValidator(string_to_list)] = Field(
        default_factory=list
    )
    annotation_method_title: Annotated[list[str], BeforeValidator(string_to_list)] = (
        Field(default_factory=list)
    )
    input_label: Annotated[list[str], BeforeValidator(string_to_list)] = Field(
        default_factory=list
    )
    input_label_prefix: str | None = Field(None)
    input_file_pattern: str | None = Field(None)


class Image(ResultData):
    specimen_title: str | None = Field(None)
    biosample_title: Annotated[list[str], BeforeValidator(string_to_list)] = Field(
        default_factory=list
    )
    image_acquisition_protocol_title: Annotated[
        list[str], BeforeValidator(string_to_list)
    ] = Field(default_factory=list)
    specimen_imaging_preparation_protocol_title: Annotated[
        list[str], BeforeValidator(string_to_list)
    ] = Field(default_factory=list)


class Annotation(ResultData):
    pass


class DatasetFile(ClosedBaseModel, FileReferenceMixin):
    pass


class Dataset(ClosedBaseModel):
    id: str | None = Field(None)
    title: str = Field()
    assigned_dataset_rembis: list[
        BioSampleReference
        | ImageAcquisitionProtocolReference
        | SpecimenImagingPreparationProtocolReference
        | ProtocolReference
        | AnnotationMethodReference
        | ImageAnalysisMethodReference
        | ImageCorrelationMethodReference
    ] = Field(default_factory=list)
    assigned_images: list[Image] = Field(default_factory=list)
    assigned_annotations: list[Annotation] = Field(default_factory=list)
    additional_files: list[DatasetFile] = Field(default_factory=list)


class Proposal(ClosedBaseModel):
    accession_id: str = Field()
    paper_doi: str = Field()
    rembis: RembiByType = Field()
    dataset_rembis: DatasetRembiByType | None = Field(None)
    datasets: list[Dataset] = Field()
