import logging
from collections import Counter
from pathlib import Path

from bia_ro_crate.models.ro_crate_models import ROCrateCreativeWork

from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Submission,
    load_submission,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    find_section_types_recursive,
    find_sections_recursive,
)
from ro_crate_ingest.biostudies_to_ro_crate.entity_conversion import (
    affiliation,
    contributor,
    dataset,
    external_reference,
    file_list,
    study,
)
from ro_crate_ingest.biostudies_to_ro_crate.entity_conversion import dataset
from ro_crate_ingest.biostudies_to_ro_crate.entity_conversion import file_list
from ro_crate_ingest.biostudies_to_ro_crate.entity_conversion.rembi_mifa_mapping import (
    AnnotationMethodMapper,
    BioSampleTaxonMapper,
    GrowthProtocolMapper,
    ImageAcquisitionProtocolMapper,
    ImageAnalysisMethodMapper,
    ImageCorrelationMethodMapper,
    ProtocolMapper,
    SpecimenImagingPreprationProtocolMapper,
    utils,
)
from ro_crate_ingest.ro_crate_defaults import (
    create_ro_crate_folder,
    get_default_context,
    write_ro_crate_metadata,
)

logger = logging.getLogger("__main__." + __name__)


def convert_biostudies_to_ro_crate(
    accession_id: str,
    crate_path: Path | None,
    fail_on_unprocessed_sections: bool = False,
):
    try:
        # Get information from biostudies
        submission = load_submission(accession_id)
    except AssertionError:
        logger.error("Failed to retrieve information from BioStudies")
        logging.exception("message")
        return

    # Raise error if there are sections that will not be processed
    section_types_not_processed = [
        f"{section}: {n}" for section, n in get_unprocessed_section_types(submission)
    ]
    if section_types_not_processed:
        unprocessed_str = "\n".join(section_types_not_processed)
        message = f"The following section types cannot be processed:\nsection type: n_occurences\n{unprocessed_str}"
        if fail_on_unprocessed_sections:
            raise ValueError(message)
        else:
            logger.warning(message)

    ro_crate_dir = create_ro_crate_folder(accession_id, crate_path)

    graph = []

    association_map = utils.initialise_association_map()

    graph += ImageAnalysisMethodMapper().get_mapped_objects(submission, association_map)
    graph += ImageCorrelationMethodMapper().get_mapped_objects(
        submission, association_map
    )
    graph += GrowthProtocolMapper().get_mapped_objects(submission, association_map)
    graph += BioSampleTaxonMapper().get_mapped_objects(submission, association_map)
    graph += SpecimenImagingPreprationProtocolMapper().get_mapped_objects(
        submission, association_map
    )
    graph += AnnotationMethodMapper().get_mapped_objects(submission, association_map)

    graph += ImageAcquisitionProtocolMapper().get_mapped_objects(
        submission, association_map
    )
    graph += ProtocolMapper().get_mapped_objects(submission, association_map)

    dataset_mapper = dataset.DatasetMapper()
    datasets = dataset_mapper.get_mapped_objects(submission, association_map)
    graph += datasets

    file_list_mapper = file_list.FileListMapper(ro_crate_dir)
    graph += file_list_mapper.get_mapped_objects(
        submission, dataset_mapper.get_accno_lookup(), dataset_mapper.get_type_lookup()
    )

    roc_affiliation_by_accno = affiliation.get_affiliations_by_accno(submission)
    graph += roc_affiliation_by_accno.values()

    roc_contributors = contributor.get_contributors(
        submission,
        roc_affiliation_by_accno,
    )
    graph += roc_contributors

    roc_external_references = external_reference.get_external_references(submission)
    graph += roc_external_references

    roc_study = study.get_study(
        submission,
        roc_contributors,
        datasets,
        file_list_mapper.COMBINED_FILE_LIST_ID,
        roc_external_references,
    )
    graph.append(roc_study)

    graph.append(ROCrateCreativeWork())
    context = get_default_context()

    write_ro_crate_metadata(ro_crate_dir, context, graph)


def get_unprocessed_section_types(submission: Submission) -> list[tuple]:
    """Return count of types of unprocessed sections"""

    convertible_section_types = [
        c.lower()
        for c in [
            "organisation",
            "organization",
            "Annotations",
            "Biosample",
            "author",
            "Study Component",
            "Associations",
            "Imaging Method",
            "Image acquisition",
            "Image analysis",
            "Image correlation",
            "Specimen",
            "Protocol",
            "Study",
            "Organism",
        ]
    ]
    section_types_in_submission = set(find_section_types_recursive(submission.section))
    unprocessed_section_types = [
        section_type
        for section_type in section_types_in_submission
        if section_type not in convertible_section_types
    ]

    non_empty_unprocessed_sections = Counter()
    for section_type in unprocessed_section_types:
        sections = find_sections_recursive(
            submission.section,
            [
                section_type,
            ],
            [],
        )
        for section in sections:
            if not section.is_empty():
                non_empty_unprocessed_sections.update(
                    [
                        section.type,
                    ]
                )

    return non_empty_unprocessed_sections.most_common()
