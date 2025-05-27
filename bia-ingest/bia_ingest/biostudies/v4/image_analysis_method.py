from bia_ingest.bia_object_creation_utils import dict_map_to_api_models
from bia_ingest.biostudies.api import Submission
from bia_ingest.biostudies.submission_parsing_utils import (
    attributes_to_dict,
    case_insensitive_get,
    find_sections_recursive,
)


from bia_shared_datamodels import semantic_models


from typing import Dict


def get_image_analysis_method_as_map(
    submission: Submission, result_summary: dict
) -> Dict[str, semantic_models.ImageAnalysisMethod]:
    image_analysis_sections = find_sections_recursive(
        submission.section, ["Image analysis"]
    )

    key_mapping = [
        # TODO: Confirm mapping with FS, AK and TZ
        ("title", "Title", None),
        ("protocol_description", "Image analysis overview", None),
        # ("features_analysed", "Image analysis overview", None),
    ]

    model_dicts_map = {}
    for section in image_analysis_sections:
        attr_dict = attributes_to_dict(section.attributes)

        model_dict = {
            k: case_insensitive_get(attr_dict, v, default)
            for k, v, default in key_mapping
        }

        model_dicts_map[attr_dict["Title"]] = model_dict

    return dict_map_to_api_models(
        model_dicts_map,
        semantic_models.ImageAnalysisMethod,
        result_summary[submission.accno],
    )
