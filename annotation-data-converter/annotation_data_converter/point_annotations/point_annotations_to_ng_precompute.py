import bia_integrator_api.models as APIModels
import pandas as pd
import logging
from bia_integrator_api.api import PrivateApi
from neuroglancer import CoordinateSpace, write_annotations
from typing import Optional
from annotation_data_converter.point_annotations.ProcessingMode import (
    PointAnnotationKeyMap,
)

logger = logging.getLogger("__main__." + __name__)


def fetch_dependencies(
    annotation_data_uuid: str, image_representation_uuid: str, api_client: PrivateApi
) -> tuple[
    APIModels.ImageRepresentation,
    APIModels.Image,
    APIModels.AnnotationData,
    APIModels.FileReference,
]:
    image_rep = api_client.get_image_representation(image_representation_uuid)
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

    annotation_data = api_client.get_annotation_data(annotation_data_uuid)
    annotation_data_creation_process = api_client.get_creation_process(
        annotation_data.creation_process_uuid
    )

    if image_uuid not in annotation_data_creation_process.input_image_uuid:
        raise ValueError(
            f"Annotation data {annotation_data_uuid} is not connected to image representation {image_representation_uuid} through creation process input image."
        )

    if len(annotation_data.original_file_reference_uuid) != 1:
        raise RuntimeError(
            f"Expected 1 original file reference for the annotation data, got: {annotation_data.original_file_reference_uuid}"
        )

    annotation_data_file_reference = [
        api_client.get_file_reference(uuid)
        for uuid in annotation_data.original_file_reference_uuid
    ]

    return (image_rep, image, annotation_data, annotation_data_file_reference)


def filter_point_annotation_data(
    point_annotation_data: pd.DataFrame,
    proposal: dict,
    annotation_file_reference: APIModels.FileReference,
    image: APIModels.Image,
    pa_key_map: PointAnnotationKeyMap,
) -> pd.DataFrame:
    annotation_file_ref_path = annotation_file_reference.file_path
    proposal_annotation_object = get_proposal_annotation_object(
        proposal, annotation_file_ref_path
    )

    if not proposal_annotation_object:
        raise RuntimeError(
            "Was not able to find a matching annotation object in proposal"
        )

    filter_key = None
    for ref_dict in proposal_annotation_object.get("input_image_label", ()):
        if ref_dict.get("label") == image.label:
            filter_key = ref_dict.get("column_id_lookup")

    if filter_key == None:
        raise RuntimeError("Unable to find filter key for annotation data.")

    return point_annotation_data.loc[
        point_annotation_data[pa_key_map.image_id] == filter_key
    ]


def get_proposal_annotation_object(proposal, file_ref_path) -> Optional[dict]:
    for dataset in proposal.get("datasets", ()):
        for annotation in dataset.get("assigned_annotations", ()):
            if annotation["file_pattern"] == file_ref_path:
                return annotation


def convert_starfile_df_to_ng_precomp(
    filtered_dataframe: pd.DataFrame,
    ng_output_dirpath: str,
    image_rep: APIModels.ImageRepresentation,
    pa_key_map: PointAnnotationKeyMap,
):

    scales = [
        image_rep.voxel_physical_size_x,
        image_rep.voxel_physical_size_y,
        image_rep.voxel_physical_size_z,
    ]

    coordinate_space = CoordinateSpace(
        names=["z", "y", "x"],
        units=["m", "m", "m"],
        scales=scales,
    )

    writer = write_annotations.AnnotationWriter(
        coordinate_space=coordinate_space, annotation_type="point"
    )

    def create_point(row: pd.Series, writer: write_annotations.AnnotationWriter):
        x = int(row.get(pa_key_map.x))
        y = int(row.get(pa_key_map.y))
        z = int(row.get(pa_key_map.z))
        writer.add_point([z, y, x])

    filtered_dataframe.apply(create_point, axis=1, args=(writer,))

    writer.write(ng_output_dirpath)
