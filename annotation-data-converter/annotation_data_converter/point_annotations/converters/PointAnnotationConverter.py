import pandas as pd
import bia_integrator_api.models as APIModels
import logging

from bia_converter.ng_overlay import get_image_info_from_ome, get_dimensions
from annotation_data_converter.point_annotations.Proposal import PointAnnotationProposal
from pathlib import Path
from neuroglancer import CoordinateSpace, write_annotations
from typing import Optional, List, Tuple
from annotation_data_converter.point_annotations.neuroglancer import (
    BASE_URI, 
    InvlerpParameters, 
    Layer, 
    ViewerState, 
    state_to_ng_uri,
)

logger = logging.getLogger(__name__)


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

    def get_image_bounds(self) -> Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]:
        
        x_bounds = (0, self.image_representation.size_x - 1)
        y_bounds = (0, self.image_representation.size_y - 1)
        z_bounds = (0, self.image_representation.size_z - 1)
        
        return (x_bounds, y_bounds, z_bounds)

    def check_points_within_bounds(
        self, 
    ) -> List[Tuple[int, Tuple[float, float, float]]]:
        """
        Check if all points fall within specified 3D bounds.
        
        Returns:
            List of tuples (row_index, (x, y, z)) for points that fall outside bounds.
            Empty list if all points are within bounds.
        """
        
        bounds = self.get_image_bounds()
        x_bounds, y_bounds, z_bounds = bounds

        x_values = self.point_annotation_data[self.proposal.x_column].values
        y_values = self.point_annotation_data[self.proposal.y_column].values
        z_values = self.point_annotation_data[self.proposal.z_column].values
        
        out_of_bounds = []
        for i in range(len(x_values)):
            x, y, z = x_values[i], y_values[i], z_values[i]
            
            if not (x_bounds[0] <= x <= x_bounds[1] and
                    y_bounds[0] <= y <= y_bounds[1] and
                    z_bounds[0] <= z <= z_bounds[1]):
                out_of_bounds.append((x, y, z))
        
        return out_of_bounds

    def validate_points(
        self, 
    ) -> bool:
        """
        Validate that all points are within bounds and raise error if issues.
        """

        out_of_bounds = self.check_points_within_bounds()
        if out_of_bounds:
            bounds = self.get_image_bounds()
            
            error_lines = [
                f"Found {len(out_of_bounds)} annotation point(s) outside image bounds.",
                f"Image bounds: x={bounds[0]}, y={bounds[1]}, z={bounds[2]}",
                "\nOut of bounds points:"
            ]
            
            for point in out_of_bounds[:5]:
                error_lines.append(f"  {point}")
            
            if len(out_of_bounds) > 5:
                error_lines.append(f"  ... and {len(out_of_bounds) - 5} more")
            
            raise ValueError("\n".join(error_lines))
            
        logger.info(f"All {len(self.point_annotation_data)} points are within bounds")
        return True

    def convert_to_neuroglancer_precomputed(
        self, 
        ng_output_dirpath: Path,
    ):

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

    def generate_neuroglancer_view_link(
        self,
        precomp_annotation_uri: str, 
        annotation_color: str = "#FFFF00"
    ) -> str:
        """
        Generate a Neuroglancer link for viewing the source image with point annotations.
        
        Args:
            ome_zarr_uri: URI to the OME-Zarr source image
            precomp_annotation_uri: URI to the precomputed format annotations 
                                   (typically the output of convert_to_neuroglancer_precomputed)
            scale_level: Which resolution level to use from the pyramid
            annotation_color: Hex color for annotation points
        
        Returns:
            Neuroglancer URL string
        """

        local_zarr_path = f"/Users/rookyard/projects/simple-ome-zarr-server/images/zarr/{self.image_representation.uuid}.zarr/0/"
        local_zarr_uri = f"http://localhost:8081/images/zarr/{self.image_representation.uuid}.zarr/0"

        file_uri_list = self.image_representation.file_uri
        if len(file_uri_list) != 1:
            raise NotImplementedError(
                "Cannot handle cases where starfile annotation data is made up of more than one image representation."
            )
        contrast_bounds, image_resolution, voxels, channel_info = get_image_info_from_ome(
            local_zarr_path, 
        )
        
        x_res, y_res, z_res = image_resolution
        lower_bound, upper_bound = contrast_bounds
        
        # neuroglancer dimensions format
        dimensions = get_dimensions(voxels)
        
        # sensible defaults (?)
        position = [0, 0, 0, int(y_res/2), int(x_res/2)]
        
        max_res = max(x_res, y_res)
        cross_section_scale = 0.5 * (max_res / 100) ** 0.6
        cross_section_scale = min(cross_section_scale, 3)
        
        # layout dependent on presence of z dim 
        has_z_dims = int(voxels['z']) != 1 and int(z_res) != 1
        display_dimensions = ["x", "y", "z"] if has_z_dims else ["x", "y"]
        layout = "4panel" if has_z_dims else "xy"
        
        shader_controls = {
            "normalized": InvlerpParameters(
                range=(lower_bound, upper_bound),
                window=None,
                channel=None
            )
        }

        base_layer = Layer(
            type="image",
            source=f"{local_zarr_uri}/|zarr2:",
            name="image",
            volumeRendering=False,
            shaderControls=shader_controls
        )
        
        annotations_layer = Layer(
            type="annotation",
            source=f"precomputed://{precomp_annotation_uri}",
            tab="annotations",
            name="particles",
            annotationColor=annotation_color
        )
        
        v = ViewerState(
            dimensions=dimensions,
            displayDimensions=display_dimensions,
            position=position,
            crossSectionScale=cross_section_scale,
            layers=[base_layer, annotations_layer],
            layout=layout
        )
        
        logger.info(f"NG LINK: {state_to_ng_uri(v, BASE_URI)}")
