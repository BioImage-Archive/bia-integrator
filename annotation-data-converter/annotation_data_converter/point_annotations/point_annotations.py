import bia_integrator_api.models as APIModels
import logging
from bia_integrator_api.api import PrivateApi

from annotation_data_converter.point_annotations.Proposal import (
    PointAnnotationProposal, GroupedPointAnnotationProposal
)
from annotation_data_converter.point_annotations.converters import (
    CSVConverter,
    StarFileConverter,
    PointAnnotationConverter,
)
from uuid import UUID

logger = logging.getLogger("__main__." + __name__)


def fetch_api_object_dependencies(
    annotation_data_uuid: UUID, image_representation_uuid: UUID, api_client: PrivateApi
) -> tuple[
    APIModels.ImageRepresentation,
    APIModels.Image,
    APIModels.AnnotationData,
    APIModels.FileReference,
]:
    image_rep = api_client.get_image_representation(str(image_representation_uuid))
    if not all(
        [
            image_rep.voxel_physical_size_x,
            image_rep.voxel_physical_size_y,
            image_rep.voxel_physical_size_z,
        ]
    ):
        raise ValueError(
            f"Image representation {image_representation_uuid} does not have all voxel physical sizes, which are required for conversion."
        )

    image_uuid = image_rep.representation_of_uuid
    image = api_client.get_image(image_uuid)

    annotation_data = api_client.get_annotation_data(str(annotation_data_uuid))
    annotation_data_creation_process = api_client.get_creation_process(
        annotation_data.creation_process_uuid
    )

    if (
        not annotation_data_creation_process.input_image_uuid
        or image_uuid not in annotation_data_creation_process.input_image_uuid
    ):
        raise ValueError(
            f"Annotation data {annotation_data_uuid} is not connected to image representation {image_representation_uuid} through creation process input image."
        )

    if len(annotation_data.original_file_reference_uuid) != 1:
        raise ValueError(
            f"Expected 1 original file reference for the annotation data, got: {annotation_data.original_file_reference_uuid}"
        )

    annotation_data_file_reference = api_client.get_file_reference(
        annotation_data.original_file_reference_uuid[0]
    )

    return (image_rep, image, annotation_data, annotation_data_file_reference)


def create_converter(
    image_representation: APIModels.ImageRepresentation,
    annotation_data_file_reference: APIModels.FileReference,
    proposal: PointAnnotationProposal,
) -> PointAnnotationConverter.PointAnnotationConverter:

    if proposal.mode == "star":
        return StarFileConverter.StarFileConverter(
            proposal=proposal,
            image_representation=image_representation,
            annotation_data_file_reference=annotation_data_file_reference,
        )
    elif proposal.mode == "csv":
        return CSVConverter.CSVConverter(
            proposal=proposal,
            image_representation=image_representation,
            annotation_data_file_reference=annotation_data_file_reference,
        )
    else:
        raise NotImplementedError()


def collect_proposals(list_of_group_proposals: list[dict]) -> list [PointAnnotationProposal]:
    proposal_list: list[PointAnnotationProposal] = []
    for proposal_group in list_of_group_proposals:
        proposal_group = GroupedPointAnnotationProposal(**proposal_group)
        proposal_list.extend(proposal_group.flatten())
    
    return proposal_list