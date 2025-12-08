from __future__ import annotations

from typing import Optional, Dict, List, Tuple
import urllib

from pydantic import BaseModel


class InvlerpParameters(BaseModel):
    range: tuple[float, float] | tuple[int, int] | None
    window: tuple[float, float] | tuple[int, int] | None
    channel: list[int] | None

ShaderControls = dict[str, float | InvlerpParameters]

class Layer(BaseModel):
    type: str
    name: str
    annotationColor: Optional[str] = None
    source: Optional[str] = None
    localDimensions: Dict[str, Tuple[int, str]] = None
    localPosition: Optional[List[int]] = []
    tab: str = "Source"
    opacity: int=1
    blend: str = "additive"
    shader: Optional[str]  = None
    shaderControls: ShaderControls | None = None
    volumeRendering: bool = True


class ViewerState(BaseModel):
    dimensions: Optional[Dict[str, Tuple[float, str]]] = None
    displayDimensions: Optional[List[str]] = None
    position: Optional[List[float]] = None
    crossSectionScale: Optional[float] = None
    projectionOrientation: Optional[List[float]] = None
    projectionScale: Optional[float] = None
    layers: List[Layer]
    layout: str = "4panel"
        
        
def state_to_ng_uri(
        state: ViewerState, 
        base_uri: str = "https://neuroglancer-demo.appspot.com/#!"
) -> str:
    viewer_json_str = state.json(exclude_none=True)
    viewer_state_no_spaces = viewer_json_str.replace(" ", "")
    
    neuroglancer_uri = base_uri + urllib.parse.quote_plus(viewer_state_no_spaces, safe=":/#")
    
    return neuroglancer_uri
