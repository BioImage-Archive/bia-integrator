from pydantic import Field, AnyUrl, ConfigDict, BaseModel
from typing_extensions import Annotated, Optional
from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
from bia_shared_datamodels.linked_data.pydantic_ld.FieldContext import FieldContext
from bia_shared_datamodels.linked_data.pydantic_ld.LDModel import ObjectReference


# Studies and Publications


class Study(ROCrateModel):
    title: Annotated[str, FieldContext("http://schema.org/name")] = Field()
    contributor: Annotated[
        list[ObjectReference],
        FieldContext("http://schema.org/author", is_id_field=True),
    ] = Field(min_length=1)
    description: Annotated[str, FieldContext("http://schema.org/description")] = Field()
    licence: Annotated[AnyUrl, FieldContext("http://schema.org/license")] = Field()
    datePublished: Annotated[str, FieldContext("http://schema.org/datePublished")] = (
        Field()
    )
    keyword: Annotated[list[str], FieldContext("http://schema.org/keywords")] = Field(
        default_factory=list
    )
    acknowledgement: Annotated[
        Optional[str], FieldContext("http://bia/acknowledgement")
    ] = Field(default=None)
    hasPart: Annotated[
        list[ObjectReference],
        FieldContext("http://schema.org/hasPart", is_id_field=True),
    ] = Field()
    accessionId: Annotated[str, FieldContext("http://schema.org/identifier")] = Field()

    model_config = ConfigDict(model_type="http://bia/Study")


class Publication(ROCrateModel):
    title: Annotated[str, FieldContext("http://schema.org/name")] = Field()
    authorNames: Annotated[str, FieldContext("http://bia/authorNames")] = Field()

    model_config = ConfigDict(model_type="http://bia/Publication")


# Contributors and Affiliations


class Contributor(ROCrateModel):
    displayName: Annotated[str, FieldContext("http://schema.org/name")] = Field()
    address: Annotated[Optional[str], FieldContext("http://schema.org/address")] = (
        Field(default=None)
    )
    website: Annotated[Optional[AnyUrl], FieldContext("http://bia/website")] = Field(
        default=None
    )
    affiliation: Annotated[
        list[ObjectReference],
        FieldContext("http://schema.org/memberOf"),
    ] = Field(default_factory=list)
    role: Annotated[list[str], FieldContext("http://bia/role")] = Field(
        default_factory=list
    )
    contactEmail: Annotated[Optional[str], FieldContext("http://schema.org/email")] = (
        Field(default=None)
    )

    model_config = ConfigDict(model_type="http://bia/Contributor")


class Affiliaton(ROCrateModel):
    displayName: Annotated[str, FieldContext("http://schema.org/name")] = Field()
    address: Annotated[Optional[str], FieldContext("http://schema.org/address")] = (
        Field(default=None)
    )
    website: Annotated[Optional[AnyUrl], FieldContext("http://bia/website")] = Field(
        default=None
    )

    model_config = ConfigDict(model_type="http://bia/Affiliation")


# Grants and funding


class Grant(ROCrateModel):
    pass

    model_config = ConfigDict(model_type="http://bia/Grant")


class FundingBody(ROCrateModel):
    pass

    model_config = ConfigDict(model_type="http://bia/FundingBody")


# External References


class ExternalReference(ROCrateModel):
    link: Annotated[AnyUrl, FieldContext("http://schema.org/url")] = Field()
    linkDescription: Annotated[
        Optional[str], FieldContext("http://schema.org/description")
    ] = Field(default=None)

    model_config = ConfigDict(model_type="http://bia/ExternalReference")


# Datasets and associations?


class Dataset(ROCrateModel):
    title: Annotated[str, FieldContext("http://schema.org/name")] = Field()
    description: Annotated[
        Optional[str], FieldContext("http://schema.org/description")
    ] = Field(default=None)
    associatedBiologicalEntity: Annotated[
        list[ObjectReference],
        FieldContext("http://bia/associatedBiologicalEntity", is_id_field=True),
    ] = Field(default_factory=list)
    associatedSpecimenImagingPreparationProtocol: Annotated[
        list[ObjectReference],
        FieldContext(
            "http://bia/associatedImagingPreparationProtocol", is_id_field=True
        ),
    ] = Field(default_factory=list)
    associatedSpecimen: Annotated[
        Optional[ObjectReference],
        FieldContext("http://bia/associatedSubject", is_id_field=True),
    ] = Field(default=None)
    associatedImageAcquisitionProtocol: Annotated[
        list[ObjectReference],
        FieldContext("http://bia/associatedImageAcquisitionProtocol", is_id_field=True),
    ] = Field(default_factory=list)
    associatedAnnotationMethod: Annotated[
        list[ObjectReference],
        FieldContext("http://bia/associatedAnnotationMethod", is_id_field=True),
    ] = Field(default_factory=list)
    associatedImageAnalysisMethod: Annotated[
        list[ObjectReference],
        FieldContext("http://bia/associatedAnalysisMethod", is_id_field=True),
    ] = Field(default_factory=list)
    associatedImageCorrelationMethod: Annotated[
        list[ObjectReference],
        FieldContext("http://bia/associatedCorrelationMethod", is_id_field=True),
    ] = Field(default_factory=list)
    associatedProtocol: Annotated[
        list[ObjectReference],
        FieldContext("http://bia/associatedProtocol", is_id_field=True),
    ] = Field(default_factory=list)
    hasPart: Annotated[
        list[ObjectReference],
        FieldContext("http://schema.org/hasPart", is_id_field=True),
    ] = Field(default_factory=list)
    associationFileMetadata: Annotated[
        Optional[ObjectReference],
        FieldContext("http://bia/associationFileMetadata", is_id_field=True),
    ] = Field(default=None)

    model_config = ConfigDict(model_type="http://bia/Dataset")


# File List


class FileList(ROCrateModel):

    tableSchema: Annotated[
        ObjectReference,
        FieldContext("http://www.w3.org/ns/csvw#tableSchema", is_id_field=True),
    ] = Field()

    model_config = ConfigDict(model_type="http://bia/FileList")


class TableSchema(ROCrateModel):
    column: Annotated[
        list[ObjectReference],
        FieldContext("http://www.w3.org/ns/csvw#column", is_id_field=True),
    ] = Field()

    model_config = ConfigDict(model_type="http://www.w3.org/ns/csvw#Schema")


class Column(ROCrateModel):
    columnName: Annotated[
        str,
        FieldContext("http://www.w3.org/ns/csvw#name"),
    ] = Field()
    propertyUrl: Annotated[
        Optional[str],
        FieldContext("http://www.w3.org/ns/csvw#propertyUrl"),
    ] = Field(default=None)

    model_config = ConfigDict(model_type="http://www.w3.org/ns/csvw#Column")


# Images, Image represntations, AnnotationData


class Image(ROCrateModel):

    resultOf: Annotated[
        ObjectReference, FieldContext("http://bia/resultOf", is_id_field=True)
    ] = Field(default=None)
    label: Annotated[Optional[str], FieldContext("http://schema.org/name")] = Field(
        default=None
    )

    model_config = ConfigDict(model_type="http://bia/Image")


class AnnotationData(ROCrateModel):
    resultOf: Annotated[
        ObjectReference, FieldContext("http://bia/resultOf", is_id_field=True)
    ] = Field(default=None)
    label: Annotated[Optional[str], FieldContext("http://schema.org/name")] = Field(
        default=None
    )
    model_config = ConfigDict(model_type="http://bia/AnnotationData")


# CreationProcess, Specimen


class Specimen(ROCrateModel):
    biologicalEntity: Annotated[
        list[ObjectReference], FieldContext("http://bia/sampleOf", is_id_field=True)
    ] = Field(default_factory=list)
    imagingPreparationProtocol: Annotated[
        list[ObjectReference],
        FieldContext("http://bia/imagingPreparationProtocol", is_id_field=True),
    ] = Field(default_factory=list)

    model_config = ConfigDict(model_type="http://bia/Specimen")


class CreationProcess(ROCrateModel):
    imageAcquisitionProtocol: Annotated[
        list[ObjectReference],
        FieldContext("http://bia/imageAcquisitionProtocol", is_id_field=True),
    ] = Field(default_factory=list)
    subject: Annotated[
        Optional[ObjectReference], FieldContext("http://bia/subject", is_id_field=True)
    ] = Field(default=None)
    protocol: Annotated[
        list[ObjectReference], FieldContext("http://bia/protocol", is_id_field=True)
    ] = Field(default_factory=list)
    annotationMethod: Annotated[
        list[ObjectReference],
        FieldContext("http://bia/annotationMethod", is_id_field=True),
    ] = Field(default_factory=list)
    inputImage: Annotated[
        list[ObjectReference], FieldContext("http://bia/inputImage", is_id_field=True)
    ] = Field(default_factory=list)

    model_config = ConfigDict(model_type="http://bia/CreationProcess")


# BioSample, Taxon


class BioSample(ROCrateModel):
    title: Annotated[Optional[str], FieldContext("http://schema.org/name")] = Field(
        default=None
    )
    biologicalEntityDescription: Annotated[
        str, FieldContext("http://bia/biologicalEntityDescription")
    ] = Field()
    experimentalVariableDescription: Annotated[
        list[str], FieldContext("http://bia/experimentalVariableDescription")
    ] = Field(default_factory=list)
    extrinsicVariableDescription: Annotated[
        list[str], FieldContext("http://bia/extrinsicVariableDescription")
    ] = Field(default_factory=list)
    intrinsicVariableDescription: Annotated[
        list[str], FieldContext("http://bia/intrinsicVariableDescription")
    ] = Field(default_factory=list)
    organismClassification: Annotated[
        list[ObjectReference], FieldContext("http://bia/organismClassification")
    ] = Field(default_factory=list)
    growthProtocol: Annotated[
        Optional[ObjectReference],
        FieldContext("http://bia/growthProtocol", is_id_field=True),
    ] = Field(default=None)

    model_config = ConfigDict(model_type="http://bia/BioSample")


class Taxon(ROCrateModel):
    commonName: Annotated[Optional[str], FieldContext("http://bia/commonName")] = Field(
        default=None
    )
    scientificName: Annotated[
        Optional[str], FieldContext("http://bia/scientificName")
    ] = Field(default=None)

    model_config = ConfigDict(model_type="http://bia/Taxon")


# Protocols, Signal-channel information for specimen preparation


class ProtocolMixin(BaseModel):
    title: Annotated[Optional[str], FieldContext("http://schema.org/name")] = Field(
        default=None
    )
    protocolDescription: Annotated[
        str, FieldContext("http://schema.org/description")
    ] = Field()


class Protocol(ProtocolMixin, ROCrateModel):

    model_config = ConfigDict(model_type="http://bia/Protocol")


class SpecimenImagingPreparationProtocol(ProtocolMixin, ROCrateModel):
    signalChannelInformation: Annotated[
        list[ObjectReference],
        FieldContext("http://bia/signalChannelInformation", is_id_field=True),
    ] = Field(default_factory=list)

    model_config = ConfigDict(
        model_type="http://bia/SpecimenImagingPreparationProtocol"
    )


class SignalChannelInformation(ROCrateModel):
    signalContrastMechanismDescription: Annotated[
        Optional[str], FieldContext("http://bia/signalContrastMechanismDescription")
    ] = Field(default=None)
    channelContentDescription: Annotated[
        Optional[str], FieldContext("http://bia/channelContentDescription")
    ] = Field(default=None)
    channelBiologicalEntity: Annotated[
        Optional[str], FieldContext("http://bia/channelBiologicalEntity")
    ] = Field(default=None)
    channelLabel: Annotated[
        Optional[str], FieldContext("http://purl.org/dc/terms/identifier")
    ] = Field(default=None)

    model_config = ConfigDict(model_type="http://bia/SignalChannel")


class ImageAcquisitionProtocol(ProtocolMixin, ROCrateModel):
    imagingInstrumentDescription: Annotated[
        str, FieldContext("http://bia/imagingInstrumentDescription")
    ] = Field()
    imagingMethodName: Annotated[
        list[str], FieldContext("http://bia/imagingMethodName")
    ] = Field(default_factory=list)
    fbbiId: Annotated[list[str], FieldContext("http://bia/fbbiId")] = Field(
        default=list
    )

    model_config = ConfigDict(model_type="http://bia/ImageAcquisitionProtocol")


class AnnotationMethod(ProtocolMixin, ROCrateModel):
    annotationCriteria: Annotated[
        Optional[str], FieldContext("http://bia/annotationCriteria")
    ] = Field(default=None)
    annotationCoverage: Annotated[
        Optional[str], FieldContext("http://bia/annotationCoverage")
    ] = Field(default=None)
    transformationDescription: Annotated[
        Optional[str], FieldContext("http://bia/transformationDescription")
    ] = Field(default=None)
    spatialInformation: Annotated[
        Optional[str], FieldContext("http://bia/spatialInformation")
    ] = Field(default=None)
    methodType: Annotated[
        list[str], FieldContext("http://bia/annotationMethodType")
    ] = Field(default_factory=list)
    annotationSourceIndicator: Annotated[
        Optional[str], FieldContext("http://bia/annotationSourceIndicator")
    ] = Field(default=None)

    model_config = ConfigDict(model_type="http://bia/AnnotationMethod")


class ImageAnalysisMethod(ProtocolMixin, ROCrateModel):
    featuresAnalysed: Annotated[
        Optional[str], FieldContext("http://bia/featuresAnalysed")
    ] = Field(default=None)

    model_config = ConfigDict(model_type="http://bia/ImageAnalysisMethod")


class ImageCorrelationMethod(ProtocolMixin, ROCrateModel):
    fiducialsUsed: Annotated[
        Optional[str], FieldContext("http://bia/fiducialsUsed")
    ] = Field(default=None)
    transformationMatrix: Annotated[
        Optional[str], FieldContext("http://bia/transformationMatrix")
    ] = Field(default=None)

    model_config = ConfigDict(model_type="http://bia/ImageCorrelationMethod")
