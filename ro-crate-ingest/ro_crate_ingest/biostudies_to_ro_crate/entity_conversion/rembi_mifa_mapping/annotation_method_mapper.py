import logging
from urllib.parse import quote

from bia_shared_datamodels import ro_crate_models

from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Section,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    attributes_to_dict,
)

from .simple_mapper import SimpleMapper

logger = logging.getLogger("__main__." + __name__)


class AnnotationMethodMapper(SimpleMapper):
    section_type = "Annotations"

    def get_mapped_object(
        self,
        section: Section,
    ) -> ro_crate_models.AnnotationMethod:
        attr_dict = attributes_to_dict(section.attributes)

        model_dict = {
            "@id": f"#{quote(section.accno)}",
            "@type": ["bia:AnnotationMethod"],
            "title": attr_dict["title"],
            "protocolDescription": attr_dict.get("annotation method", ""),
            "methodType": self._get_annotation_type(attr_dict),
            "annotation_criteria": attr_dict.get("annotation criteria", None),
            "annotation_coverage": attr_dict.get("annotation coverage", None),
        }

        return ro_crate_models.AnnotationMethod(**model_dict)

    @staticmethod
    def _get_annotation_type(attr_dict: dict):
        annotation_types = attr_dict.get("annotation type", "")
        if annotation_types:
            if isinstance(annotation_types, str):
                annotation_types = [at.strip() for at in annotation_types.split(",")]
        else:
            annotation_types = ["other"]
        return annotation_types
