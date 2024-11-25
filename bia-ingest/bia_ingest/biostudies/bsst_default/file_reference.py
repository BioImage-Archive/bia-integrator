import logging
from pydantic import ValidationError
from typing import List, Dict, Optional

from ...bia_object_creation_utils import dict_to_uuid, filter_model_dictionary
from ..submission_parsing_utils import (
    find_datasets_with_file_lists,
    attributes_to_dict,
    find_sections_recursive,
)
from ..api import (
    Submission,
    file_uri,
    flist_from_flist_fname,
)
from .. import api  # To make reference to biostudies.File explicit
from bia_shared_datamodels import bia_data_model, semantic_models
from ...persistence_strategy import PersistenceStrategy

logger = logging.getLogger("__main__." + __name__)


def get_file_reference_from_files(
    submission: Submission,
    study: bia_data_model.Study,
    result_summary: dict,
    persister: Optional[PersistenceStrategy] = None,
):
    study = find_sections_recursive(submission.section, ["Study"])
    files = study.files
    logger.debug(files)
