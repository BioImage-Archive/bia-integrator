import json
import ngff_zarr as nz
from pathlib import Path
from numpy import percentile
import urllib.parse
import typer
from typing_extensions import Annotated

app = typer.Typer()

def generate_image_map(images):
    ## Study specific filter to remove certain images from S-BIAD634
    FILTER = [
        "Raw image in JPEG format",
        "Visualization of groundtruth masks in PNG format",
        "Visualization of groundtruth for randomly selected nuclei in PNG format"
    ]
    def has_filtered_description(metadata, filter_list):
        return any(
            md.get("value", {}).get("attributes", {}).get("file description") in filter_list
            for md in metadata
        )

    def is_valid_rep(rep):
        return (
            rep.get("image_format") == ".ome.zarr" and
            not has_filtered_description(img.get("additional_metadata", []), FILTER)
        )
    
    def check_voxels(voxels):
        return [1e-6 if voxel is None else voxel for voxel in voxels]

    def get_voxels_from_image_rep(image_rep):
        return check_voxels((image_rep["voxel_physical_size_x"], image_rep["voxel_physical_size_y"], image_rep["voxel_physical_size_z"], image_rep["size_c"], image_rep["size_t"]))
    
    def file_filter(img):
        return not has_filtered_description(img.get("additional_metadata", []), FILTER)
    
    annotated_images_map = {}
    
    for img in images.values():
        input_image_uuid = img.get("creation_process", {}).get("input_image_uuid", [])
        if not input_image_uuid or not file_filter(img):
            continue
        key = input_image_uuid[0]
        if key not in images:
            continue

        valid_rep_source = [rep for rep in images[key].get("representation", []) if is_valid_rep(rep)]
        if not valid_rep_source:
            continue

        source_rep = valid_rep_source[0]
        source_url = source_rep["file_uri"][0]
        source_voxel = get_voxels_from_image_rep(source_rep)

        if key not in annotated_images_map:
            annotated_images_map[key] = {
                "source_url": source_url,
                "source_voxel": source_voxel,
                "annotations": []
            }

        annotations = [
            {
                "url": rep["file_uri"][0],
                "voxels": get_voxels_from_image_rep(rep)
            }
            for rep in img.get("representation", []) if is_valid_rep(rep)
        ]

        if not annotations:
            continue

        annotated_images_map[key]["annotations"].append({
            "annotation_uuid": img["uuid"],
            "annotation_url": [ann["url"] for ann in annotations],
            "annotation_voxels": [ann["voxels"] for ann in annotations]
        })

    return annotated_images_map

def write_json(filepath: Path, data: dict):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

def read_json(path):
    with open(path) as f:
        return json.load(f)

def get_contrast_and_xyz_dims(source_url, scale_level=0, use_percentiles=True):
    source = nz.from_ngff_zarr(source_url)
    image = source.images[scale_level]
    data = image.data
    x, y, z = data.shape[-1], data.shape[-2], data.shape[-3]

    if use_percentiles:
        min_val = percentile(data.__array__(), 1)
        max_val = percentile(data.__array__(), 99)
    else:
        min_val = min(data.__array__())
        max_val = max(data.__array__())
        
    return [[min_val, max_val], [x,y,z]]

def get_dimensions(dims):
    dims = process_xy_voxels(dims)
    units = "m" if dims[0] < 1 else "um"
    return {
            "t": [dims[4], ""],
            "c": [dims[3], ""],
            "z": [float(dims[2]), ""],
            "y": [float(dims[1]), units],
            "x": [float(dims[0]), units]
        }

def get_tranformations(output_dims, input_dims):
    return {
        "outputDimensions": get_dimensions(output_dims),
        "inputDimensions": get_dimensions(input_dims)
    }

def get_transformed_layer(source, source_voxel, annotated_voxel):
    return {"url": f"{source}/|zarr2:", "transform": get_tranformations(source_voxel, annotated_voxel)}

def get_layer(source, layer_type, name, source_voxel, annotated_voxels, contrast=None):
    if annotated_voxels:
        if source_voxel[0] >= annotated_voxels[0]:
            source_transformation =  get_transformed_layer(source, annotated_voxels, source_voxel)
        else:
            source_transformation =  get_transformed_layer(source, source_voxel, source_voxel)

    shaders = {"normalized": {"range": contrast}} if layer_type == "image" else {}
    return {
        "type": layer_type,
        "source": source_transformation,
        "name": name,
        "tab": "source" if layer_type == "image" else "segments",
        "shaderControls": shaders,
        "segments": [] if layer_type == "segmentation" else None
    }

def convert_voxel_size_to_um(vx):
    return vx * 1e-6 if int(vx) == 1 else vx

def process_xy_voxels(obj):
    for i in range(2):  # Only x and y
        obj[i] = convert_voxel_size_to_um(obj[i])
    return obj

def generate_neuroglancer_url(source_url, segmentation_urls, source_voxel=(1,1,1,1,1), annotation_voxels=[(1,1,1,1,1)], layout="xy"):
    source_label = "Source Image"
    contrast, xyz = get_contrast_and_xyz_dims(source_url)
    x,y,z = xyz
    layers = [get_layer(source_url, "image", source_label, source_voxel, annotation_voxels[0], contrast)]
    dimensions = get_dimensions(source_voxel)

    for i, seg_url in enumerate(segmentation_urls):
        layers.append(get_layer(seg_url, "segmentation", f"Annotation {i+1}", source_voxel, annotation_voxels[i]))

    imageHasZDims = int(source_voxel[2]) != 1 and int(annotation_voxels[0][2]) != 1 and int(z) != 1
    
    display_dimension = ["x", "y", "z"] if imageHasZDims else ["x", "y"]
    layout = "4panel-alt" if imageHasZDims else "xy" 
    position = [0, 0, 0, int(y/2), int(x/2)] if imageHasZDims else [0, 0, int(y/2), int(x/2)]
    cross_section_scale = 3 if int(x) > 2000 else 1


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
def main(images_path: Path = typer.Option(..., help="Path to raw OME-Zarr JSON")):
    annotated_image_map = generate_image_map(read_json(images_path))

    uuid_to_skip = []
    overlays = {}

    for key, values in annotated_image_map.items():
        if key in uuid_to_skip or not values:
            continue

        source_image_url = values["source_url"]
        source_voxels = values["source_voxel"]

        if not source_image_url:
            continue

        annotated_images = values["annotations"]
        annotation_urls = [a["annotation_url"][0] for a in annotated_images if a["annotation_url"]]
        annotation_voxels = [a["annotation_voxels"][0] for a in annotated_images if a["annotation_voxels"]]

        if not annotation_voxels:
            print(f"Skipping {key} due to missing annotation voxels.")
            continue
        url = generate_neuroglancer_url(source_image_url, annotation_urls, source_voxels, annotation_voxels)
        overlays[key] = url

    write_json("overlay_neuroglancer_links.json", overlays)


if __name__ == "__main__":
    app()
