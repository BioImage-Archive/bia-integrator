import json
import ngff_zarr as nz
from numpy import percentile
import urllib.parse
import typer
from typing_extensions import Annotated

app = typer.Typer()

def getContrastValues(source_url, scale_level=0, use_percentiles=True):
    source = nz.from_ngff_zarr(source_url)
    image = source.images[scale_level]
    data = image.data
    
    if use_percentiles:
        min_val = percentile(data.__array__(), 1)
        max_val = percentile(data.__array__(), 99)
    else:
        min_val = min(data.__array__())
        max_val = max(data.__array__())
        
    return[min_val, max_val]

def getDimensions(dims):
    dims = processXYVoxels(dims)
    units = "m" if dims[0] < 1 else "um"
    return {
            "t": [dims[4], ""],
            "c": [dims[3], ""],
            "z": [float(dims[2]), ""],
            "y": [float(dims[1]), units],
            "x": [float(dims[0]), units]
        }

def getTranformations(output_dims, input_dims):
    return {
        "outputDimensions": getDimensions(output_dims),
        "inputDimensions": getDimensions(input_dims)
    }

def getTransformedLayer(source, source_voxel, annotated_voxel):
    return {"url": f"{source}/|zarr2:", "transform": getTranformations(source_voxel, annotated_voxel)}

def getLayer(source, layer_type, name, source_voxel, annotated_voxels=None):
    if annotated_voxels:
        if source_voxel[0] > annotated_voxels[0]:
            source_transformation =  getTransformedLayer(source, annotated_voxels, source_voxel)
        elif source_voxel[0] == annotated_voxels[0]:
            source_transformation = getTransformedLayer(source, annotated_voxels, source_voxel)
        else:
            source_transformation =  getTransformedLayer(source, source_voxel, source_voxel)
    shaders = {"normalized": {"range": getContrastValues(source)}} if layer_type == "image" else {}
    return {
        "type": layer_type,
        "source": source_transformation,
        "name": name,
        "tab": "source" if layer_type == "image" else "segments",
        "shaderControls": shaders,
        "segments": [] if layer_type == "segmentation" else None
    }

def convertVoxelSizeToUM(vx):
    return vx * 1e-6 if int(vx) == 1 else vx

def processXYVoxels(obj):
    for i in range(2):  # Only x and y
        obj[i] = convertVoxelSizeToUM(obj[i])
    return obj

def generateNeuroglancerUrl(source_url, segmentation_urls, source_voxel=(1,1,1,1,1), annotation_voxels=[(1,1,1,1,1)], layout="xy"):
    source_label = "Source Image"
    layers = [getLayer(source_url, "image", source_label, source_voxel, annotation_voxels[0])]
    dimensions = getDimensions(source_voxel)

    for i, seg_url in enumerate(segmentation_urls):
        layers.append(getLayer(seg_url, "segmentation", f"Annotation {i+1}", source_voxel, annotation_voxels[i]))

    display_dimension = ["x", "y", "z"] if int(source_voxel[2]) != 1 else ["x", "y"]
    layout = "4panel-alt" if int(source_voxel[2]) != 1 else "xy" 

    state = {
        "dimensions": dimensions,
        "displayDimensions": display_dimension,
        "position": [0, 0, 1, 1],
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
         source_voxel: Annotated[str, typer.Argument(..., help="source image voxels")],
         annotation_voxels: Annotated[str, typer.Argument(..., help="a List of annotated image voxels")],
         ):
    
    url = generateNeuroglancerUrl(source, segmentation, source_voxel, annotation_voxels)
    return url

if __name__ == "__main__":
    app()
