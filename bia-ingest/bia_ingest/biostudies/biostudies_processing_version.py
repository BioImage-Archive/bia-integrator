from enum import Enum

import logging


logger = logging.getLogger("__main__." + __name__)


class BioStudiesProcessingVersion(str, Enum):
    """Wether to process all file references, ask if there are a lot of files, or always skip."""

    V4 = "v4"
    BIOSTUDIES_DEFAULT = "biostudies_default"
    FALLBACK = "fallback"
