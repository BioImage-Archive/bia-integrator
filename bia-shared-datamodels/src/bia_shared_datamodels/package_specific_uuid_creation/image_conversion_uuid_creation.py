from uuid import UUID
from bia_shared_datamodels import uuid_creation, attribute_models
from bia_shared_datamodels.semantic_models import Provenance
from .shared import create_unique_str_attribute


def create_image_representation_uuid(
    study_uuid: str, conversion_process_dict: dict
) -> tuple[UUID, attribute_models.DocumentUUIDUinqueInputAttribute]:
    """
    An example conversion_process_dict is:

    {
        "image_representation_of_submitted_by_uploader": f"{input_image_rep.uuid}",
        "conversion_function": {
            "conversion_function": "bioformats2raw",
            "version": get_bioformats2raw_version(),
        },
        "conversion_config": conversion_parameters,
    }
    """
    unique_string = f"{conversion_process_dict}"
    return (
        uuid_creation.create_image_representation_uuid(
            study_uuid=study_uuid, unique_string=unique_string
        ),
        create_unique_str_attribute(unique_string, Provenance.bia_image_conversion),
    )
