from pydantic import BaseModel, Field
from bia_shared_datamodels.ro_crate_models import Taxon

class Specimen(BaseModel):
    title: str = Field()
    biosample_title: str = Field()
    specimen_imaging_preparation_protocol_title: str = Field()


class BioSample(BaseModel):
    title: str = Field()
    biological_entity_description: str = Field()
    organism_classification: list[Organism] = Field()


class SpecimenImagingPreparationProtocol(BaseModel):
    pass


class RembiByType(BaseModel):
    BioSample: list[BioSample] = Field()
    SpecimenImagingPreparationProtocol: list[SpecimenImagingPreparationProtocol] = (
        Field()
    )
    Specimen: list[Specimen] = Field()
    ImageAcquisitionProtocol: list[ImageAcquisitionProtocol] = Field()
    AnnotationMethod: list[AnnotationMethod] = Field()
    Protocol: list[Protocol] = Field()


class ResultData(BaseModel):
    label_prefix: str | None = Field(None)
    file_pattern: str | None = Field(None)
    specimen_title: str | None = Field(None)
    protocol_title: str | None = Field(None)
    annotation_method_title: str | None = Field(None)
    input_label_prefix: str | None = Field(None)
    input_file_pattern: str | None = Field(None)


class Image(ResultData):
    pass


class Annotation(ResultData):
    pass


class Dataset(BaseModel):
    title: str = Field()
    assigned_dataset_rembis: list[str] = Field(default_factory=list)
    assigned_images: list[Image] = Field(default_factory=list)
    assigned_annotations: list[Annotation] = Field(default_factory=list)


class Proposal(BaseModel):
    accession_id: str = Field()
    paper_doi: str = Field()
    rembis: RembiByType = Field()
    datasets: list[Dataset] = Field()
