import json
import ngff_zarr as nz
import urllib.parse
import typer
from typing import List, Optional
from typing_extensions import Annotated
from numpy import percentile
import logging
from rich.logging import RichHandler

app = typer.Typer()

logging.basicConfig(
    level=logging.INFO, format="%(message)s", handlers=[RichHandler(show_time=False)]
)

logger = logging.getLogger()

def get_voxels_from_scales(scales, units, data):
    """
    Gets voxel values using scales and axis units and uses image data to get 
    number of channels and time-steps
    """
    t, c = data[0], data[1]
    voxels = {}
    for key in scales.keys():
        if key in units.keys():
            au = 1e-6 if units[key] == 'micrometer' else 1
            scale = scales[key]
            voxels[key] = scale * au
    voxels['t'], voxels['c'] = t, c
    return voxels

def get_image_info_from_ome(
        source_url: str,
        scale_level: int = 0,
        use_percentiles: bool = False
    ) -> List:
    """
    Compute contrast range (min, max), spatial dimensions (x, y, z), voxels and channel information
    for a given OME-Zarr source.

    Args:
        source_url (str): URL of the source OME-Zarr image.
        scale_level (int): Downsample level to use from the image pyramid.
        use_percentiles (bool): Whether to compute contrast using percentiles (1% and 99%).

    Returns:
        Tuple: ([min_val, max_val], [x, y, z], voxels, channel_info)
    """
    source = nz.from_ngff_zarr(source_url)
    image = source.images[scale_level]
    scales = image.scale
    axes_units = image.axes_units
    data = image.data

    channel_info = {}
    if (omero := getattr(source.metadata, "omero", None)) and omero.channels:
        for ch in omero.channels:
            label = ch.label.replace("C:", "").replace("Channel ", "")
            channel_info[int(label)] = {
                "color": ch.color,
                "min": ch.window.min,
                "max": ch.window.max
            }

    voxels = get_voxels_from_scales(scales, axes_units, data.shape)
    
    x, y, z = data.shape[-1], data.shape[-2], data.shape[-3]

    if use_percentiles:
        min_val = percentile(data.__array__(), 1)
        max_val = percentile(data.__array__(), 99)
    else:
        min_val = min(data.__array__().flatten())
        max_val = max(data.__array__().flatten())
    return [[int(min_val), int(max_val)], [x,y,z], voxels, channel_info]

def get_dimensions(dims: dict):
    dims = process_xy_voxels(dims)
    units = "m" if dims['x'] < 1 else "um"
    return {
            "t": [dims['t'], ""],
            "c": [dims['c'], ""],
            "z": [float(dims['z']), ""],
            "y": [float(dims['y']), units],
            "x": [float(dims['x']), units]
        }

def get_transformations(
        output_dims: dict,
        input_dims: dict
    ) -> dict:
    return {
        "outputDimensions": get_dimensions(output_dims),
        "inputDimensions": get_dimensions(input_dims)
    }

def get_transformed_layer(
        source: str,
        source_voxel: dict,
        annotated_voxel: dict
    ) -> dict:
    return {"url": f"{source}/|zarr2:", "transform": get_transformations(source_voxel, annotated_voxel)}

def get_layer(
        source: str,
        layer_type: str,
        name: str,
        source_voxel: dict,
        annotated_voxel: dict,
        channel: int = 0,
        contrast: Optional[List[float]] = None,
        channel_info : Optional[dict] = None
    ) -> dict:
    if annotated_voxel:
        if source_voxel['x'] >= annotated_voxel['x']:
            source_transformation =  get_transformed_layer(source, annotated_voxel, source_voxel)
        else:
            source_transformation =  get_transformed_layer(source, source_voxel, source_voxel)
    
    if source_voxel['c'] > 1 and layer_type == "image" and channel_info:
        channel_map = {0: "r", 1: "g", 2: "b"}
        min, max = channel_info[channel]['min'], channel_info[channel]['max']
        shader = f"#uicontrol float channel_min slider(min={min}, max={max}, default={min})\n#uicontrol float channel_max slider(min={min}, max={max}, default={max})\n#uicontrol float channel_intensity slider(min=0, max=2, default=1)\n"
        shader = shader + "void main() {\nfloat r = 0.0, g = 0.0, b = 0.0, channel = 0.0;\nfloat scale = channel_max - channel_min;\nif (scale > 0.0){\nfloat norm = clamp((float(getDataValue(0).value) - channel_min) / scale, 0.0, 1.0);\nchannel += norm * channel_intensity;\n}\n" 
        selected_channel = channel_map[channel]
        shader = str(shader + f"{selected_channel} = channel;\n" + "emitRGB(vec3(clamp(r, 0.0, 1.0), clamp(g, 0.0, 1.0), clamp(b, 0.0, 1.0)));\n}")
        shaderControls = "shader"
    else:
        shader = {"normalized": {"range": contrast}} if layer_type == "image" else {}
        shaderControls = "shaderControls"
    layer_dict = {
        "type": layer_type,
        "source": source_transformation,
        "name": name,
        "tab": "source" if layer_type == "image" else "segments",
        f"{shaderControls}": shader,
        "segments": [] if layer_type == "segmentation" else None,
        "localPosition": [channel],
    }

    if source_voxel['c'] > 1 and layer_type == "image":
        layer_dict["blend"] = "additive"
        layer_dict["opacity"] =  1

    return layer_dict

def convert_voxel_size_to_um(vx: float) -> float:
    return vx * 1e-6 if int(vx) == 1 else vx

def process_xy_voxels(obj: dict) -> dict:
    obj['x'] = convert_voxel_size_to_um(obj['x'])
    obj['y'] = convert_voxel_size_to_um(obj['y'])
    return obj

def generate_neuroglancer_url(
        source_url: str,
        segmentation_urls: List[str],
        layout: str = "xy"
    ) -> str:
    """
    Generate a Neuroglancer URL to visualize the source image and segmentation layers.

    Args:
        source_url (str): The URL of the source OME-Zarr image.
        segmentation_urls (List[str]): URLs of segmentation annotations.
        source_voxel (Tuple[float, float, float, int, int], optional): Voxel sizes of the source image.
        annotation_voxels (List[Tuple[float, float, float, int, int]], optional): Voxel sizes of the segmentations.
        layout (str, optional): Layout style for Neuroglancer.

    Returns:
        str: Neuroglancer-compatible URL.
    """
    layers = []
    source_label = "Source Image"
    source_contrast, image_resolution, source_voxel, source_channel_info = get_image_info_from_ome(source_url)
    x_res, y_res, z_res = image_resolution
    
    dimensions = get_dimensions(source_voxel)

    for i, seg_url in enumerate(segmentation_urls):
        contrast, annotation_image_shape, annotation_voxel, annotation_channel_info = get_image_info_from_ome(seg_url)
        if i == 0:
            if source_voxel['c'] > 1:
                for channel in range(source_voxel['c']):
                    layers.append(get_layer(source_url, "image", f"{source_label}-channel-{channel}", source_voxel, annotation_voxel, channel, source_contrast, source_channel_info))
            else:
                layers.append(get_layer(source_url, "image", source_label, source_voxel, annotation_voxel, 0, source_contrast))
            imageHasZDims = int(source_voxel['z']) != 1 and int(annotation_voxel['z']) != 1 and int(z_res) != 1
        layers.append(get_layer(seg_url, "segmentation", f"Annotation {i+1}", source_voxel, annotation_voxel))


    display_dimension = ["x", "y", "z"] if imageHasZDims else ["x", "y"]
    layout = "4panel-alt" if imageHasZDims else "xy" 
    position = [0, 0, 0, int(y_res/2), int(x_res/2)]

    max_res = max(x_res, y_res)
    cross_section_scale = 0.5 * (max_res / 100) ** 0.6
    cross_section_scale = min(cross_section_scale, 3)


    state = {
        "dimensions": dimensions,
        "displayDimensions": display_dimension,
        "position": position,
        "crossSectionScale": cross_section_scale,
        "projectionScale": 512,
        "layers": layers,
        "layout": layout
    }

    json_str = json.dumps(state, separators=(",", ":"))
    encoded_json = urllib.parse.quote(json_str)
    return f"https://neuroglancer-demo.appspot.com/#!{encoded_json}"

@app.command()
def main(
    source_image_url: Annotated[
        str, typer.Option("--source-image-url", help="S3 url for the source image")
    ],
    annotation_image_urls: Annotated[
        List[str], typer.Option("--annotation-image-urls", help="S3 url for One or more annotation image")
    ],
    layout: Annotated[
        str, typer.Option("--layout", help="Neuroglancer layout (e.g., xy, 4panel-alt)")
    ] = "xy"
):

    """
    Generate a Neuroglancer URL from a source image and annotation images.
    """
    url = generate_neuroglancer_url(source_image_url, annotation_image_urls, layout) 
    print(url) # For now just print the neuroglancer link this will get added to the image object later.   


if __name__ == "__main__":
    app()