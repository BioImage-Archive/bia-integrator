from __future__ import annotations

from typing import Optional, Dict, List, Tuple
import urllib

from pydantic import BaseModel

BASE_URI = "https://neuroglancer-demo.appspot.com/#!"
# class Dimension(BaseModel):
#     Tuple[str]

COLOR_SHADER = "#define true 1\n#define false 0\n\n#uicontrol invlerp normalized\n#uicontrol vec3 color color()\n#uicontrol float attenuation slider(min=1, max=50, step=1)\n#uicontrol float contrast slider(min=-3, max=3, step=0.01)\n  \nvoid main() {\n  \n#if VOLUME_RENDERING\n  float alpha = pow(normalized(), 1.0 / attenuation) * exp(contrast);\n  alpha = pow(alpha, attenuation);\n  emitRGBA(vec4(color, alpha));\n#else\n  float value = normalized() * exp(contrast);\n  emitRGB(color*value);\n#endif\n}"
# DEFAULT_SHADER = "#define true 1\n#define false 0\n\n#uicontrol invlerp normalized\n#uicontrol vec3 color color(default=\"white\")\n#uicontrol float attenuation slider(min=1, max=50, step=1)\n#uicontrol float contrast slider(min=-3, max=3, step=0.01)\n  \nvoid main() {\n  \n#if VOLUME_RENDERING\n  float alpha = pow(normalized(), 1.0 / attenuation) * exp(contrast);\n  alpha = pow(alpha, attenuation);\n  emitRGBA(vec4(color, alpha));\n#else\n  float value = normalized() * exp(contrast);\n  emitRGB(color*value);\n#endif\n}"

# class ShaderControls(BaseModel):
#     normalized: Dict[str, List[int]]
#     color: Optional[str] = None
#     attenuation: Optional[int] = None
#     contrast: Optional[float] = None


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
        
        
def state_to_ng_uri(state: ViewerState, base_uri=BASE_URI) -> str:
    viewer_json_str = state.json(exclude_none=True)
    viewer_state_no_spaces = viewer_json_str.replace(" ", "")
    
    neuroglancer_uri = base_uri + urllib.parse.quote_plus(viewer_state_no_spaces, safe=":/#")
    
    return neuroglancer_uri