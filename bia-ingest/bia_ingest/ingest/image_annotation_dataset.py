import logging
from typing import List, Any, Dict, Optional

from ..bia_object_creation_utils import (
    dict_to_uuid,
    dicts_to_api_models,
    filter_model_dictionary,
)

from ..cli_logging import log_model_creation_count
from .biostudies.submission_parsing_utils import (
    find_sections_recursive,
    attributes_to_dict,
)
import bia_ingest.ingest.study as study_conversion
from .biostudies.api import (
    Submission,
)
from bia_shared_datamodels import bia_data_model
from ..persistence_strategy import PersistenceStrategy


logger = logging.getLogger("__main__." + __name__)


def get_image_annotation_dataset(
    submission: Submission,
    result_summary: dict,
    persister: Optional[PersistenceStrategy] = None,
) -> List[bia_data_model.ImageAnnotationDataset]:
    iad_model_dicts = extract_image_annotation_dataset_method_dicts(submission)
    image_annotation_datasets = dicts_to_api_models(
        iad_model_dicts,
        bia_data_model.ImageAnnotationDataset,
        result_summary[submission.accno],
    )

    log_model_creation_count(
        bia_data_model.ImageAnnotationDataset,
        len(image_annotation_datasets),
        result_summary[submission.accno],
    )

    if persister and image_annotation_datasets:
        persister.persist(image_annotation_datasets)

    return image_annotation_datasets


def extract_image_annotation_dataset_method_dicts(
    submission: Submission,
) -> List[Dict[str, Any]]:
    annotation_sections = find_sections_recursive(
        submission.section, ["Annotations"], []
    )

    model_dicts = []
    for section in annotation_sections:
        attr_dict = attributes_to_dict(section.attributes)

        # TODO: there is no "Description" field in the biostudies model.
        # We should probably decide how we want to map the overview between here and the AnotationMethod.
        model_dict = {
            "title_id": attr_dict.get("Title", ""),
            "description": attr_dict.get("Description"),
            "submitted_in_study_uuid": study_conversion.get_study_uuid(submission),
            "example_image_uri": [],
            "version": 0,
            "attribute": {},
        }

        model_dict["accno"] = section.__dict__.get("accno", "")
        model_dict["accession_id"] = submission.accno
        model_dict["uuid"] = generate_annotation_method_uuid(model_dict)
        model_dict = filter_model_dictionary(
            model_dict, bia_data_model.ImageAnnotationDataset
        )

        model_dicts.append(model_dict)

    return model_dicts


def generate_annotation_method_uuid(protocol_dict: Dict[str, Any]) -> str:
    attributes_to_consider = [
        "accession_id",
        "accno",
        "title_id",
    ]
    return dict_to_uuid(protocol_dict, attributes_to_consider)
