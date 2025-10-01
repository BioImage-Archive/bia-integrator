import pandas as pd
import bia_integrator_api.models as APIModels
from annotation_data_converter.point_annotations.Proposal import PointAnnotationProposal
from pathlib import Path
from neuroglancer import CoordinateSpace, write_annotations


class PointAnnotationConverter:
    """
    Superclass of all point annotation converters.
    load() should be overridden by more specific classes that can handle specific data files.
    Methods that transform the data one loaded into a Dataframe should be written here.
    """

    proposal: PointAnnotationProposal
    image_representation: APIModels.ImageRepresentation
    annotation_data_file_reference: APIModels.FileReference
    point_annotation_data: pd.DataFrame

    def __init__(
        self,
        proposal: PointAnnotationProposal,
        image_representation: APIModels.ImageRepresentation,
        annotation_data_file_reference: APIModels.FileReference,
    ):
        self.proposal = proposal
        self.image_representation = image_representation
        self.annotation_data_file_reference = annotation_data_file_reference
        self.point_annotation_data = pd.DataFrame()

    def load(self):
        raise NotImplementedError(
            f"Do not instanciate {self.__class__.__name__} directly: use subclasses that are data format specific."
        )

    def convert_to_neuroglancer_precomputed(self, ng_output_dirpath: Path):

        scales = [
            self.image_representation.voxel_physical_size_x,
            self.image_representation.voxel_physical_size_y,
            self.image_representation.voxel_physical_size_z,
        ]

        coordinate_space = CoordinateSpace(
            names=["z", "y", "x"],
            units=["m", "m", "m"],
            scales=scales,
        )

        writer = write_annotations.AnnotationWriter(
            coordinate_space=coordinate_space, annotation_type="point"
        )

        def create_point(
            row: pd.Series,
            writer: write_annotations.AnnotationWriter,
            x_column: str | int,
            y_column: str | int,
            z_column: str | int,
        ):
            x = int(row[x_column])
            y = int(row[y_column])
            z = int(row[z_column])
            writer.add_point([z, y, x])

        self.point_annotation_data.apply(
            create_point,
            axis=1,
            args=(
                writer,
                self.proposal.x_column,
                self.proposal.y_column,
                self.proposal.z_column,
            ),
        )

        writer.write(ng_output_dirpath)
