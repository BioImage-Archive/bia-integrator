import json
import urllib.parse
import typer
from typing_extensions import Annotated

app = typer.Typer()

def get_tranformations(src, ann):
    return {
        "outputDimensions": {
            "t": [src[4], ""],
            "c": [src[3], ""],
            "z": [float(src[2]), ""],
            "y": [float(src[1]), "um"],
            "x": [float(src[0]), "um"]
        },
        "inputDimensions": {
            "t": [ann[4], ""],
            "c": [ann[3], ""],
            "z": [float(ann[2]), ""],
            "y": [float(ann[1]), "um"],
            "x": [float(ann[0]), "um"]
        }
    }

def get_layer(source, layer_type, name, voxel_size, annotated_voxels=None):
    if annotated_voxels:
        return {
            "type": layer_type,
            "source": {
                "url": f"{source}/|zarr2:",
                "transform": get_tranformations(voxel_size, annotated_voxels)
            },
            "name": name,
            "tab": "source" if layer_type == "image" else "segments",
            "segments": [] if layer_type == "segmentation" else None
        }
    else:
        return {
            "type": layer_type,
            "source": f"{source}/|zarr2:",
            "name": name,
            "tab": "source" if layer_type == "image" else "segments",
            "segments": [] if layer_type == "segmentation" else None
        }

def convertVoxelSizeToUM(vx):
    return vx * 1e-6 if int(vx) == 1 else vx

def processXYVoxels(obj):
    for i in range(2):  # Only x and y
        obj[i] = convertVoxelSizeToUM(obj[i])
    return obj

def generate_neuroglancer_url(source_url, segmentation_urls, voxel_size=(1,1,1,1,1), annotated_voxel_size=[(1,1,1,1,1)], layout="xy"):
    source_label = "Source Image"
    src_vx = voxel_size
    ann_vx = annotated_voxel_size[0]

    if voxel_size[0] > ann_vx[0]:
        layers = [get_layer(source_url, "image", source_label, ann_vx, voxel_size)]
    elif voxel_size[0] == ann_vx[0]:
        layers = [get_layer(source_url, "image", source_label, voxel_size)]
    else:
        layers = [get_layer(source_url, "image", source_label, voxel_size, ann_vx)]

    dimensions = {
        "x": [float(src_vx[0]), "um"],
        "y": [float(src_vx[1]), "um"],
        "z": [float(src_vx[2]), ""],
        "c": [float(src_vx[3]), ""],
        "t": [float(src_vx[4]), ""]
    }

    for i, seg_url in enumerate(segmentation_urls):
        if voxel_size[0] < annotated_voxel_size[i][0]:
            layers.append(get_layer(seg_url, "segmentation", f"Annotation {i+1}", voxel_size, annotated_voxel_size[i]))
        else:
            layers.append(get_layer(seg_url, "segmentation", f"Annotation {i+1}", annotated_voxel_size[i]))

    state = {
        "dimensions": dimensions,
        "displayDimensions": ["x", "y"],
        "position": [1, 1, 1, 1],
        "crossSectionScale": 1,
        "projectionScale": 512,
        "layers": layers,
        "layout": layout
    }

    json_str = json.dumps(state, separators=(",", ":"))
    encoded_json = urllib.parse.quote(json_str)
    return f"https://neuroglancer-demo.appspot.com/#!{encoded_json}"

@app.command()
def main(source: Annotated[str, typer.Argument(..., help="OME ZARR URL for the source image")],
         segmentation: Annotated[str, typer.Argument(..., help="a List of OME ZARR URLs for the annotated image")],
         voxel_size: Annotated[str, typer.Argument(..., help="source image voxels")],
         annotation_voxels: Annotated[str, typer.Argument(..., help="a List of annotated image voxels")],
         ):
    
    url = generate_neuroglancer_url(source, segmentation, voxel_size, annotation_voxels)
    return url

if __name__ == "__main__":
    app()
