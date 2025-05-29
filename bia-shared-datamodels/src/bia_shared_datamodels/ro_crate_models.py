from pydantic import Field, AnyUrl, ConfigDict
from typing_extensions import Annotated, Optional
from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
from bia_shared_datamodels.linked_data.pydantic_ld.FieldContext import FieldContext
from bia_shared_datamodels.linked_data.pydantic_ld.LDModel import ObjectReference


# Studies and Publications


class Study(ROCrateModel):
    title: Annotated[str, FieldContext("http://schema.org/name")] = Field()
    contributor: Annotated[
        list[ObjectReference], FieldContext("http://schema.org/author", isIdField=True)
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
        list[ObjectReference], FieldContext("http://schema.org/hasPart", isIdField=True)
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
    address: Annotated[str, FieldContext("http://schema.org/address")] = Field(
        default=None
    )
    website: Annotated[AnyUrl, FieldContext("http://bia/website")] = Field(default=None)
    affiliation: Annotated[
        list[ObjectReference],
        FieldContext("http://schema.org/memberOf"),
    ] = Field(default_factory=list)
    role: Annotated[str, FieldContext("http://bia/role")] = Field(default=None)

    model_config = ConfigDict(model_type="http://bia/Contributor")


class Affiliaiton(ROCrateModel):
    displayName: Annotated[str, FieldContext("http://schema.org/name")] = Field()
    address: Annotated[str, FieldContext("http://schema.org/address")] = Field(
        default=None
    )
    website: Annotated[AnyUrl, FieldContext("http://bia/website")] = Field(default=None)
    affiliation: Annotated[
        list[str],
        FieldContext("http://schema.org/memberOf"),
    ] = Field(default_factory=list)

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
    associatedBioSample: Annotated[
        list[ObjectReference],
        FieldContext("http://bia/associatedBiologicalEntity", isIdField=True),
    ] = Field(default_factory=list)
    associatedSpecimenImagingPreparationProtocol: Annotated[
        list[ObjectReference],
        FieldContext("http://bia/associatedImagingPreparationProtocol", isIdField=True),
    ] = Field(default_factory=list)
    associatedSpecimen: Annotated[
        ObjectReference, FieldContext("http://bia/associatedSubject", isIdField=True)
    ] = Field(default=None)
    associatedSpecimenImageAcquisitionProtocol: Annotated[
        list[ObjectReference],
        FieldContext("http://bia/associatedImageAcquisitionProtocol", isIdField=True),
    ] = Field(default_factory=list)
    associatedAnnotationMethod: Annotated[
        list[ObjectReference],
        FieldContext("http://bia/associatedAnnotationMethod", isIdField=True),
    ] = Field(default_factory=list)
    associatedImageAnalysisMethod: Annotated[
        list[ObjectReference],
        FieldContext("http://bia/associatedAnalysisMethod", isIdField=True),
    ] = Field(default_factory=list)
    associatedImageCorrelationMethod: Annotated[
        list[ObjectReference],
        FieldContext("http://bia/associatedImageCorrelationMethod", isIdField=True),
    ] = Field(default_factory=list)
    associatedImageCorrelationMethod: Annotated[
        list[ObjectReference],
        FieldContext("http://bia/associatedProtocol", isIdField=True),
    ] = Field(default_factory=list)

    model_config = ConfigDict(model_type="http://bia/Dataset")


# Images, Image represntations


class Image(ROCrateModel):

    model_config = ConfigDict(model_type="http://bia/Image")


# CreationProcess, Specimen


class Specimen(ROCrateModel):
    biologicalEntity: Annotated[
        list[ObjectReference], FieldContext("http://bia/sampleOf", isIdField=True)
    ] = Field(default_factory=list)
    imagingPreparationProtocol: Annotated[
        list[ObjectReference],
        FieldContext("http://bia/imagingPreparationProtocol", isIdField=True),
    ] = Field(default_factory=list)

    model_config = ConfigDict(model_type="http://bia/Specimen")


class CreationProcess(ROCrateModel):
    imageAcqusitionProtocol: Annotated[
        list[ObjectReference],
        FieldContext("http://bia/imageAcquisitionProtocol", isIdField=True),
    ] = Field(default_factory=list)
    specimen: Annotated[
        Optional[ObjectReference], FieldContext("http://bia/subject", isIdField=True)
    ] = Field(default=None)
    protocol: Annotated[
        list[ObjectReference], FieldContext("http://bia/protocol", isIdField=True)
    ] = Field(default_factory=list)
    annotationMethod: Annotated[
        list[ObjectReference],
        FieldContext("http://bia/annotationMethod", isIdField=True),
    ] = Field(default_factory=list)
    inputImage: Annotated[
        list[ObjectReference], FieldContext("http://bia/inputImage", isIdField=True)
    ] = Field(default_factory=list)

    model_config = ConfigDict(model_type="http://bia/CreationProcess")


# BioSample, Taxon


class BioSample(ROCrateModel):
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
        list[ObjectReference], FieldContext("http://bia/growthProtocol", isIdField=True)
    ] = Field(default_factory=list)

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


class Protocol(ROCrateModel):
    title: Annotated[Optional[str], FieldContext("http://schema.org/name")] = Field(
        default=None
    )
    protocolDescription: Annotated[
        str, FieldContext("http://schema.org/description")
    ] = Field()

    model_config = ConfigDict(model_type="http://bia/Protocol")


class SpecimenImagingPreparationProtocol(Protocol):
    signalChannelInformation: Annotated[
        list[ObjectReference],
        FieldContext("http://bia/signalChannelInformation", isIdField=True),
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


class ImageAcquisitionProtocol(Protocol):
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


class AnnotationMethod(Protocol):
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
        Optional[str], FieldContext("http://bia/annotationMethodType")
    ] = Field(default=None)
    annotationSourceIndicator: Annotated[
        Optional[str], FieldContext("http://bia/annotationSourceIndicator")
    ] = Field(default=None)

    model_config = ConfigDict(model_type="http://bia/AnnotationMethod")


class ImageAnyalysisMethod(Protocol):
    featuresAnalysed: Annotated[
        Optional[str], FieldContext("http://bia/featuresAnalysed")
    ] = Field(default=None)

    model_config = ConfigDict(model_type="http://bia/ImageAnalysisMethod")


class ImageCorrelationMethod(Protocol):
    fiducialsUsed: Annotated[
        Optional[str], FieldContext("http://bia/fiducialsUsed")
    ] = Field(default=None)
    transformationMatrix: Annotated[
        Optional[str], FieldContext("http://bia/transformationMatrix")
    ] = Field(default=None)

    model_config = ConfigDict(model_type="http://bia/ImageCorrelationMethod")
