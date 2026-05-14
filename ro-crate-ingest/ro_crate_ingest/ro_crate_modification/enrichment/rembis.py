import logging

from bia_ro_crate.models import ro_crate_models
from bia_ro_crate.core.file_list import FileList
from bia_ro_crate.models.linked_data.pydantic_ld.LDModel import ObjectReference
from bia_ro_crate.core.bia_ro_crate_metadata import BIAROCrateMetadata
from ro_crate_ingest.ro_crate_modification.enrichment.file_list_utils import (
    ASSOCIATED_ANNOTATION_METHOD_PROPERTY,
    ASSOCIATED_BIOLOGICAL_ENTITY_PROPERTY,
    ASSOCIATED_IMAGE_ACQUISITION_PROTOCOL_PROPERTY,
    ASSOCIATED_IMAGING_PREPARATION_PROTOCOL_PROPERTY,
    ASSOCIATED_PROTOCOL_PROPERTY,
    get_dataset_column_id,
    merge_file_list_association_value,
)
from ro_crate_ingest.ro_crate_modification.enrichment.utils import (
    entity_ref,
    entity_refs,
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
    """
    entities: list[ro_crate_models.ROCrateModel] = []

    taxon_refs = []
    for taxon in biosample.organism_classification:
        taxon_id = taxon.ncbi_id or title_to_id(taxon.scientific_name)
        taxon_entity = ro_crate_models.Taxon(
            **{
                "@id": taxon_id,
                "@type": type_for(ro_crate_models.Taxon),
                "commonName": taxon.common_name,
                "scientificName": taxon.scientific_name,
            }
        )
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
        growth_protocol_ref = entity_ref(biosample.growth_protocol_title[0])

    biosample_entity = ro_crate_models.BioSample(
        **{
            "@id": title_to_id(biosample.title),
            "@type": type_for(ro_crate_models.BioSample),
            "title": biosample.title,
            "biologicalEntityDescription": biosample.biological_entity_description,
            "organismClassification": taxon_refs,
            "growthProtocol": growth_protocol_ref,
        }
    )
    entities.append(biosample_entity)
    return entities


def add_rembi_entities(
    ro_crate_metadata: BIAROCrateMetadata,
    rembis: RembiByType,
) -> None:
    """
    Add study-wide REMBI entities to the metadata graph.
    """
    for protocol in rembis.protocols:
        entity = ro_crate_models.Protocol(
            **{
                "@id": title_to_id(protocol.title),
                "@type": type_for(ro_crate_models.Protocol),
                "title": protocol.title,
                "protocolDescription": protocol.protocol_description,
            }
        )
        ro_crate_metadata.add_entity(entity)
        logger.debug(f"Added Protocol: {entity.id}")

    for biosample in rembis.biosamples:
        for entity in _make_biosample_entities(biosample):
            if isinstance(entity, ro_crate_models.Taxon):
                ro_crate_metadata.add_entity_if_absent(entity)
            else:
                ro_crate_metadata.add_entity(entity)
            logger.debug(f"Added entity: {entity.id}")

    for sipp in rembis.specimen_imaging_preparation_protocols:
        entity = ro_crate_models.SpecimenImagingPreparationProtocol(
            **{
                "@id": title_to_id(sipp.title),
                "@type": type_for(ro_crate_models.SpecimenImagingPreparationProtocol),
                "title": sipp.title,
                "protocolDescription": sipp.protocol_description,
            }
        )
        ro_crate_metadata.add_entity(entity)
        logger.debug(f"Added SpecimenImagingPreparationProtocol: {entity.id}")

    for iap in rembis.image_acquisition_protocols:
        entity = ro_crate_models.ImageAcquisitionProtocol(
            **{
                "@id": title_to_id(iap.title),
                "@type": type_for(ro_crate_models.ImageAcquisitionProtocol),
                "title": iap.title,
                "protocolDescription": iap.protocol_description,
                "imagingInstrumentDescription": iap.imaging_instrument_description,
                "imagingMethodName": iap.imaging_method_name,
                "fbbiId": iap.fbbi_id,
            }
        )
        ro_crate_metadata.add_entity(entity)
        logger.debug(f"Added ImageAcquisitionProtocol: {entity.id}")

    for annotation_method in rembis.annotation_methods:
        entity = ro_crate_models.AnnotationMethod(
            **{
                "@id": title_to_id(annotation_method.title),
                "@type": type_for(ro_crate_models.AnnotationMethod),
                "title": annotation_method.title,
                "protocolDescription": annotation_method.protocol_description,
                "methodType": annotation_method.method_type,
            }
        )
        ro_crate_metadata.add_entity(entity)
        logger.debug(f"Added AnnotationMethod: {entity.id}")


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
    updated = entity.model_copy(
        update={
            "associatedBiologicalEntity": (
                list(entity.associatedBiologicalEntity)
                + entity_refs(assoc.biosample_titles)
            ),
            "associatedImageAcquisitionProtocol": (
                list(entity.associatedImageAcquisitionProtocol)
                + entity_refs(assoc.image_acquisition_protocol_titles)
            ),
            "associatedSpecimenImagingPreparationProtocol": (
                list(entity.associatedSpecimenImagingPreparationProtocol)
                + entity_refs(assoc.specimen_imaging_preparation_protocol_titles)
            ),
            "associatedAnnotationMethod": (
                list(entity.associatedAnnotationMethod)
                + entity_refs(assoc.annotation_method_titles)
            ),
            "associatedProtocol": (
                list(entity.associatedProtocol) + entity_refs(assoc.protocol_titles)
            ),
            "associatedImageAnalysisMethod": (
                list(entity.associatedImageAnalysisMethod)
                + entity_refs(assoc.image_analysis_method_titles)
            ),
            "associatedImageCorrelationMethod": (
                list(entity.associatedImageCorrelationMethod)
                + entity_refs(assoc.image_correlation_method_titles)
            ),
        }
    )
    ro_crate_metadata.update_entity(updated)
    logger.debug(f"Applied explicit associations to dataset '{dataset_config.name}'.")


def add_dataset_associations_to_file_list(
    file_list: FileList,
    ro_crate_metadata: BIAROCrateMetadata,
    dataset_configs: list[DatasetModificationConfig],
) -> None:
    """
    Write explicit dataset associations into matching file-list columns.

    Downstream RO-Crate-to-BIA conversion treats these dataset-level associations
    as defaults for individual result-data rows only when the corresponding
    file-list column is absent. When a column already exists, blank cells would
    suppress that fallback, so materialise the dataset association there without
    adding otherwise unnecessary columns.
    """
    dataset_col_id = get_dataset_column_id(file_list)

    association_columns = [
        (
            "biosample_titles",
            ASSOCIATED_BIOLOGICAL_ENTITY_PROPERTY,
        ),
        (
            "specimen_imaging_preparation_protocol_titles",
            ASSOCIATED_IMAGING_PREPARATION_PROTOCOL_PROPERTY,
        ),
        (
            "image_acquisition_protocol_titles",
            ASSOCIATED_IMAGE_ACQUISITION_PROTOCOL_PROPERTY,
        ),
        (
            "annotation_method_titles",
            ASSOCIATED_ANNOTATION_METHOD_PROPERTY,
        ),
        (
            "protocol_titles",
            ASSOCIATED_PROTOCOL_PROPERTY,
        ),
    ]

    for dataset_config in dataset_configs:
        if dataset_config.associations is None:
            continue

        dataset_id = resolve_dataset_id_by_name(ro_crate_metadata, dataset_config.name)

        row_mask = file_list.data[dataset_col_id] == dataset_id

        for title_field, property_url in association_columns:
            titles = getattr(dataset_config.associations, title_field)
            if not titles:
                continue

            col_id = file_list.get_column_id_by_property(property_url)
            if col_id is None:
                continue

            association_ids = [title_to_id(title) for title in titles]
            file_list.data.loc[row_mask, col_id] = file_list.data.loc[
                row_mask, col_id
            ].apply(
                lambda existing: merge_file_list_association_value(
                    existing, association_ids
                )
            )
