# coding: utf-8

"""
    FastAPI

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.1.0
    Generated by: https://openapi-generator.tech
"""

from datetime import date, datetime  # noqa: F401
import decimal  # noqa: F401
import functools  # noqa: F401
import io  # noqa: F401
import re  # noqa: F401
import typing  # noqa: F401
import typing_extensions  # noqa: F401
import uuid  # noqa: F401

import frozendict  # noqa: F401

from openapi_client import schemas  # noqa: F401


class ChannelRendering(
    schemas.DictSchema
):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """


    class MetaOapg:
        required = {
            "colormap_start",
            "colormap_end",
        }
        
        class properties:
            
            
            class colormap_start(
                schemas.ListSchema
            ):
            
            
                class MetaOapg:
                    items = schemas.NumberSchema
            
                def __new__(
                    cls,
                    _arg: typing.Union[typing.Tuple[typing.Union[MetaOapg.items, decimal.Decimal, int, float, ]], typing.List[typing.Union[MetaOapg.items, decimal.Decimal, int, float, ]]],
                    _configuration: typing.Optional[schemas.Configuration] = None,
                ) -> 'colormap_start':
                    return super().__new__(
                        cls,
                        _arg,
                        _configuration=_configuration,
                    )
            
                def __getitem__(self, i: int) -> MetaOapg.items:
                    return super().__getitem__(i)
            
            
            class colormap_end(
                schemas.ListSchema
            ):
            
            
                class MetaOapg:
                    items = schemas.NumberSchema
            
                def __new__(
                    cls,
                    _arg: typing.Union[typing.Tuple[typing.Union[MetaOapg.items, decimal.Decimal, int, float, ]], typing.List[typing.Union[MetaOapg.items, decimal.Decimal, int, float, ]]],
                    _configuration: typing.Optional[schemas.Configuration] = None,
                ) -> 'colormap_end':
                    return super().__new__(
                        cls,
                        _arg,
                        _configuration=_configuration,
                    )
            
                def __getitem__(self, i: int) -> MetaOapg.items:
                    return super().__getitem__(i)
            scale_factor = schemas.NumberSchema
            __annotations__ = {
                "colormap_start": colormap_start,
                "colormap_end": colormap_end,
                "scale_factor": scale_factor,
            }
    
    colormap_start: MetaOapg.properties.colormap_start
    colormap_end: MetaOapg.properties.colormap_end
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["colormap_start"]) -> MetaOapg.properties.colormap_start: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["colormap_end"]) -> MetaOapg.properties.colormap_end: ...
    
    @typing.overload
    def __getitem__(self, name: typing_extensions.Literal["scale_factor"]) -> MetaOapg.properties.scale_factor: ...
    
    @typing.overload
    def __getitem__(self, name: str) -> schemas.UnsetAnyTypeSchema: ...
    
    def __getitem__(self, name: typing.Union[typing_extensions.Literal["colormap_start", "colormap_end", "scale_factor", ], str]):
        # dict_instance[name] accessor
        return super().__getitem__(name)
    
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["colormap_start"]) -> MetaOapg.properties.colormap_start: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["colormap_end"]) -> MetaOapg.properties.colormap_end: ...
    
    @typing.overload
    def get_item_oapg(self, name: typing_extensions.Literal["scale_factor"]) -> typing.Union[MetaOapg.properties.scale_factor, schemas.Unset]: ...
    
    @typing.overload
    def get_item_oapg(self, name: str) -> typing.Union[schemas.UnsetAnyTypeSchema, schemas.Unset]: ...
    
    def get_item_oapg(self, name: typing.Union[typing_extensions.Literal["colormap_start", "colormap_end", "scale_factor", ], str]):
        return super().get_item_oapg(name)
    

    def __new__(
        cls,
        *_args: typing.Union[dict, frozendict.frozendict, ],
        colormap_start: typing.Union[MetaOapg.properties.colormap_start, list, tuple, ],
        colormap_end: typing.Union[MetaOapg.properties.colormap_end, list, tuple, ],
        scale_factor: typing.Union[MetaOapg.properties.scale_factor, decimal.Decimal, int, float, schemas.Unset] = schemas.unset,
        _configuration: typing.Optional[schemas.Configuration] = None,
        **kwargs: typing.Union[schemas.AnyTypeSchema, dict, frozendict.frozendict, str, date, datetime, uuid.UUID, int, float, decimal.Decimal, None, list, tuple, bytes],
    ) -> 'ChannelRendering':
        return super().__new__(
            cls,
            *_args,
            colormap_start=colormap_start,
            colormap_end=colormap_end,
            scale_factor=scale_factor,
            _configuration=_configuration,
            **kwargs,
        )