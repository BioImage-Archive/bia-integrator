from uuid import UUID
from bia_shared_datamodels import uuid_creation, attribute_models
from bia_shared_datamodels.semantic_models import Provenance
from bia_shared_datamodels.package_specific_uuid_creation import shared


def create_image_representation_uuid(
    study_uuid: str, image_uuid: str
) -> tuple[UUID, attribute_models.DocumentUUIDUinqueInputAttribute]:
    """
    For creating the base represetation of image e.g. the first one, comprised of the file(s) sent to us by a contributor.
    """
    unique_string = f"{image_uuid}"
    return (
        uuid_creation.create_image_representation_uuid(
            study_uuid=study_uuid, unique_string=unique_string
        ),
        shared.create_unique_str_attribute(
            unique_string, Provenance.bia_image_assignment
        ),
    )

