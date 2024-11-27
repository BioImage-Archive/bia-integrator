from bia_ingest.biostudies.v4.study import get_study
from bia_ingest.biostudies.v4.dataset import get_dataset
from bia_ingest.biostudies.v4.bio_sample import get_bio_sample_as_map
from bia_ingest.biostudies.v4.growth_protocol import get_growth_protocol_as_map
from bia_ingest.biostudies.v4.specimen_imaging_preparation_protocol import (
    get_specimen_imaging_preparation_protocol_as_map,
)
from bia_ingest.biostudies.v4.file_reference import get_file_reference_by_dataset
from bia_ingest.biostudies.v4.image_acquisition_protocol import (
    get_image_acquisition_protocol_map,
)
from bia_ingest.biostudies.v4.annotation_method import get_annotation_method_as_map
from bia_ingest.biostudies.v4.image_analysis_method import (
    get_image_analysis_method_as_map,
)
from bia_ingest.biostudies.v4.image_correlation_method import (
    get_image_correlation_method_as_map,
)
import logging

logger = logging.getLogger("__main__." + __name__)


def process_submission_v4(submission, result_summary, process_files, persister):
    study = get_study(submission, result_summary, persister=persister)

    association_object_dict = {}
    association_object_dict["image_acquisition_protocol"] = (
        get_image_acquisition_protocol_map(
            submission, result_summary, persister=persister
        )
    )
    association_object_dict["annotation_method"] = get_annotation_method_as_map(
        submission, result_summary, persister=persister
    )
    association_object_dict["specimen_imaging_preparation_protocol"] = (
        get_specimen_imaging_preparation_protocol_as_map(
            submission, result_summary, persister=persister
        )
    )
    growth_protocol_map = get_growth_protocol_as_map(
        submission, result_summary, persister=persister
    )
    association_object_dict["growth_protocol"] = growth_protocol_map
    association_object_dict["bio_sample"] = get_bio_sample_as_map(
        submission, growth_protocol_map, result_summary, persister=persister
    )

    association_object_dict["image_analysis_method"] = get_image_analysis_method_as_map(
        submission, result_summary
    )

    association_object_dict["image_correlation_method"] = (
        get_image_correlation_method_as_map(submission, result_summary)
    )

    datasets = get_dataset(
        submission,
        association_object_dict,
        result_summary,
        persister=persister,
    )

    if process_files:
        get_file_reference_by_dataset(
            submission,
            datasets,
            result_summary,
            persister=persister,
        )
    else:
        logger.info("Skipping file reference creation.")
