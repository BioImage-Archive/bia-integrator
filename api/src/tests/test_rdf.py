from fastapi.testclient import TestClient
import pytest
import rdflib
import pathlib
import json
import uuid
from typing import List
from .util import (
    get_template_study, 
    get_template_biosample,
    get_template_image,
    get_template_file_reference,
    get_template_collection,
    get_template_specimen,
    get_template_image_acquisition
)

@pytest.fixture(scope="function")
def rdf_graph():
    return rdflib.Graph()


@pytest.mark.parametrize(
    "context_file_name, json_object_dict",
    [
        ( 'CollectionContext.jsonld', get_template_collection(add_uuid=True) ),
        ( 'StudyContext.jsonld', get_template_study(add_uuid=True) ),
        ( 'ImageContext.jsonld', get_template_image({"uuid": uuid.uuid4()}, add_uuid=True) ),
        ( 'StudyFileReferenceContext.jsonld', get_template_file_reference({"uuid": uuid.uuid4()}, add_uuid=True) ),
        ( 'BiosampleContext.jsonld', get_template_biosample(add_uuid=True) ),
        ( 'SpecimenContext.jsonld', get_template_specimen({"uuid": uuid.uuid4()}, add_uuid=True) ),
        ( 'ImageAcquisitionContext.jsonld', get_template_image_acquisition({"uuid": uuid.uuid4()}, add_uuid=True) ),
    ]
)
def test_context_creates_parseable_jsonld(rdf_graph: rdflib.Graph, context_file_name: str, json_object_dict: dict):

    context_path = pathlib.Path(pathlib.Path.cwd() / 'src/models/jsonld/1.0' / context_file_name )
    context = {}

    isParseable = False
    try:
        with open(context_path) as context_file:
            context = json.load(context_file)
        json_object_dict["@context"] = context
        rdf_graph.parse(data=json_object_dict, format="json-ld")
        isParseable = True
    except:
        isParseable = False

    assert isParseable
    assert len(rdf_graph)>0