# coding: utf-8

"""
    FastAPI

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)

    The version of the OpenAPI document: 0.1.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest
import datetime

import bia_integrator_api
from bia_integrator_api.models.bia_image_representation import BIAImageRepresentation  # noqa: E501
from bia_integrator_api.rest import ApiException

class TestBIAImageRepresentation(unittest.TestCase):
    """BIAImageRepresentation unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test BIAImageRepresentation
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `BIAImageRepresentation`
        """
        model = bia_integrator_api.models.bia_image_representation.BIAImageRepresentation()  # noqa: E501
        if include_optional :
            return BIAImageRepresentation(
                size = 56, 
                uri = [
                    ''
                    ], 
                type = '', 
                dimensions = '', 
                attributes = bia_integrator_api.models.attributes.Attributes(), 
                rendering = bia_integrator_api.models.rendering_info.RenderingInfo(
                    channel_renders = [
                        bia_integrator_api.models.channel_rendering.ChannelRendering(
                            channel_label = '', 
                            colormap_start = [
                                1.337
                                ], 
                            colormap_end = [
                                1.337
                                ], 
                            scale_factor = 1.337, )
                        ], 
                    default_z = 56, 
                    default_t = 56, )
            )
        else :
            return BIAImageRepresentation(
                size = 56,
        )
        """

    def testBIAImageRepresentation(self):
        """Test BIAImageRepresentation"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()