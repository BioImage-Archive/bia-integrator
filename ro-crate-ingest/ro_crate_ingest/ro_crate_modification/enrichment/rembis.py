import logging

from bia_shared_datamodels import ro_crate_models
from bia_shared_datamodels.linked_data.pydantic_ld.LDModel import ObjectReference
from ro_crate_ingest.bia_ro_crate.bia_ro_crate_metadata import BIAROCrateMetadata
from ro_crate_ingest.ro_crate_modification.enrichment.utils import (
    ref, 
    refs, 
    resolve_dataset_id_by_name, 
    title_to_id, 
    type_for, 
)
from ro_crate_ingest.ro_crate_modification.modification_config import (
    Biosample,
    DatasetModificationConfig, 
    RembiByType,
)

logger = logging.getLogger(__name__)


def _make_biosample_entities(
    biosample: Biosample,
) -> list[ro_crate_models.ROCrateModel]:
    """
    Build Taxon and BioSample entities for a single biosample config.
    Taxons are returned before the BioSample so they exist in the graph
    when the BioSample references them.

    Note: Taxon in ro_crate_models has no ncbi_id field; if provided in
    the config it is not currently representable in the RO-Crate entity.
    """
    entities: list[ro_crate_models.ROCrateModel] = []

    taxon_refs = []
    for taxon in biosample.organism_classification:
        taxon_entity = ro_crate_models.Taxon(**{
            "@id": title_to_id(taxon.scientific_name),
            "@type": type_for(ro_crate_models.Taxon),
            "commonName": taxon.common_name,
            "scientificName": taxon.scientific_name,
        })
        entities.append(taxon_entity)
        taxon_refs.append(ObjectReference(**{"@id": taxon_entity.id}))

    growth_protocol_ref = None
    if biosample.growth_protocol_title:
        if len(biosample.growth_protocol_title) > 1:
            logger.warning(
                f"BioSample '{biosample.title}': multiple growth_protocol_titles provided "
                f"but BioSample.growthProtocol accepts only one reference. "
                f"Using '{biosample.growth_protocol_title[0]}'."
            )
        growth_protocol_ref = ref(biosample.growth_protocol_title[0])

    biosample_entity = ro_crate_models.BioSample(**{
        "@id": title_to_id(biosample.title),
        "@type": type_for(ro_crate_models.BioSample),
        "title": biosample.title,
        "biologicalEntityDescription": biosample.biological_entity_description,
        "organismClassification": taxon_refs,
        "growthProtocol": growth_protocol_ref,
    })
    entities.append(biosample_entity)
    return entities


def apply_dataset_associations(
    ro_crate_metadata: BIAROCrateMetadata,
    dataset_config: DatasetModificationConfig,
) -> None:
    """
    Write explicit REMBI associations from the dataset's 'associations' block
    to the Dataset entity in the RO-Crate metadata graph.

    Covers the full set of association fields on the Dataset model:
    biosample, IAP, SIPP, annotation method, protocol, image analysis method,
    and image correlation method.
    """
    if dataset_config.associations is None:
        return

    dataset_id = resolve_dataset_id_by_name(ro_crate_metadata, dataset_config.name)
    if dataset_id is None:
        return

    entity = ro_crate_metadata.get_object(dataset_id)
    if not isinstance(entity, ro_crate_models.Dataset):
        logger.warning(
            f"Entity '{dataset_id}' is not a Dataset; cannot apply associations."
        )
        return

    assoc = dataset_config.associations
    updated = entity.model_copy(update={
        "associatedBiologicalEntity": (
            list(entity.associatedBiologicalEntity) + refs(assoc.biosample_titles)
        ),
        "associatedImageAcquisitionProtocol": (
            list(entity.associatedImageAcquisitionProtocol)
            + refs(assoc.image_acquisition_protocol_titles)
        ),
        "associatedSpecimenImagingPreparationProtocol": (
            list(entity.associatedSpecimenImagingPreparationProtocol)
            + refs(assoc.specimen_imaging_preparation_protocol_titles)
        ),
        "associatedAnnotationMethod": (
            list(entity.associatedAnnotationMethod) + refs(assoc.annotation_method_titles)
        ),
        "associatedProtocol": (
            list(entity.associatedProtocol) + refs(assoc.protocol_titles)
        ),
        "associatedImageAnalysisMethod": (
            list(entity.associatedImageAnalysisMethod)
            + refs(assoc.image_analysis_method_titles)
        ),
        "associatedImageCorrelationMethod": (
            list(entity.associatedImageCorrelationMethod)
            + refs(assoc.image_correlation_method_titles)
        ),
    })
    ro_crate_metadata.update_entity(updated)
    logger.debug(f"Applied explicit associations to dataset '{dataset_config.name}'.")


def add_rembi_entities(
    ro_crate_metadata: BIAROCrateMetadata,
    rembis: RembiByType,
) -> None:
    """
    Add study-wide REMBI entities to the metadata graph.
    """
    for protocol in rembis.protocols:
        entity = ro_crate_models.Protocol(**{
            "@id": title_to_id(protocol.title),
            "@type": type_for(ro_crate_models.Protocol),
            "title": protocol.title,
            "protocolDescription": protocol.protocol_description,
        })
        ro_crate_metadata.add_entity(entity)
        logger.debug(f"Added Protocol: {entity.id}")

    for biosample in rembis.biosamples:
        for entity in _make_biosample_entities(biosample):
            ro_crate_metadata.add_entity(entity)
            logger.debug(f"Added entity: {entity.id}")

    for sipp in rembis.specimen_imaging_preparation_protocols:
        entity = ro_crate_models.SpecimenImagingPreparationProtocol(**{
            "@id": title_to_id(sipp.title),
            "@type": type_for(ro_crate_models.SpecimenImagingPreparationProtocol),
            "title": sipp.title,
            "protocolDescription": sipp.protocol_description,
        })
        ro_crate_metadata.add_entity(entity)
        logger.debug(f"Added SpecimenImagingPreparationProtocol: {entity.id}")

    for iap in rembis.image_acquisition_protocols:
        entity = ro_crate_models.ImageAcquisitionProtocol(**{
            "@id": title_to_id(iap.title),
            "@type": type_for(ro_crate_models.ImageAcquisitionProtocol),
            "title": iap.title,
            "protocolDescription": iap.protocol_description,
            "imagingInstrumentDescription": iap.imaging_instrument_description,
            "imagingMethodName": iap.imaging_method_name,
            "fbbiId": iap.fbbi_id,
        })
        ro_crate_metadata.add_entity(entity)
        logger.debug(f"Added ImageAcquisitionProtocol: {entity.id}")

    for annotation_method in rembis.annotation_methods:
        entity = ro_crate_models.AnnotationMethod(**{
            "@id": title_to_id(annotation_method.title),
            "@type": type_for(ro_crate_models.AnnotationMethod),
            "title": annotation_method.title,
            "protocolDescription": annotation_method.protocol_description,
            "methodType": annotation_method.method_type,
        })
        ro_crate_metadata.add_entity(entity)
        logger.debug(f"Added AnnotationMethod: {entity.id}")
