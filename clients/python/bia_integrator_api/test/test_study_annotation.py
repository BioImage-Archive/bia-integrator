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
from bia_integrator_api.models.study_annotation import StudyAnnotation  # noqa: E501
from bia_integrator_api.rest import ApiException

class TestStudyAnnotation(unittest.TestCase):
    """StudyAnnotation unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test StudyAnnotation
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `StudyAnnotation`
        """
        model = bia_integrator_api.models.study_annotation.StudyAnnotation()  # noqa: E501
        if include_optional :
            return StudyAnnotation(
                author_email = 'jUR,rZ#UM/?R,Fp^l6$ARj@ebi.ac.uk', 
                key = '', 
                value = '', 
                state = 'active'
            )
        else :
            return StudyAnnotation(
                author_email = 'jUR,rZ#UM/?R,Fp^l6$ARj@ebi.ac.uk',
                key = '',
                value = '',
                state = 'active',
        )
        """

    def testStudyAnnotation(self):
        """Test StudyAnnotation"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()