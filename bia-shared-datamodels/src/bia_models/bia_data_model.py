import semantic_models
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID

from pydantic_core import Url


class DocumentMixin(BaseModel):
    uuid: UUID = Field()


class Study(
    semantic_models.Study,
    DocumentMixin,
):
    experimental_imaging_component: List[UUID] = Field()
    annotation_component: List[UUID] = Field()


class ImageRepresentation(
    semantic_models.ImageRepresentation,
    DocumentMixin,
):
    original_file_reference: Optional[List[UUID]] = Field()


class ExperimentalImagingDataset(
    semantic_models.ImageRepresentation,
    DocumentMixin,
):
    image: List[UUID] = Field()
    file: List[UUID] = Field()
    # we include image analysis and correlation


class ExperimentallyCapturedImage(
    semantic_models.ExperimentallyCapturedImage,
    DocumentMixin,
):
    acquisition_process: List[UUID] = Field()
    represenatation: List[UUID] = Field()
    # note Specimen is included in image document, but links to protocol & biosample via uuid.


class ImageAcquisition(
    semantic_models.ExperimentallyCapturedImage,
    DocumentMixin,
):
    pass


class SpecimenPrepartionProtocol(
    semantic_models.SpecimenPrepartionProtocol,
    DocumentMixin,
):
    pass


class Specimen(
    semantic_models.ExperimentallyCapturedImage,
):
    sample_of: List[UUID] = Field()
    preparation_method: List[UUID] = Field()


class Biosample(
    semantic_models.Biosample,
    DocumentMixin,
):
    pass


class ImageAnnotationDataset(
    semantic_models.ImageAnnotationDataset,
    DocumentMixin,
):
    image: List[UUID] = Field()
    file: List[UUID] = Field()


class AnnotationFileReference(
    semantic_models.AnnotationFileReference,
    DocumentMixin,
):
    represenatation: List[UUID] = Field()
    source_image: UUID = Field()
