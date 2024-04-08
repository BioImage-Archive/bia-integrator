import pytest
import rdflib
import json
import uuid
from .util import (
    get_template_study,
    get_template_biosample,
    get_template_image,
    get_template_file_reference,
    get_template_collection,
    get_template_specimen,
    get_template_image_acquisition,
)
import urllib


@pytest.fixture(scope="function")
def rdf_graph():
    return rdflib.Graph()


@pytest.mark.parametrize(
    "json_object_dict",
    [
        get_template_collection(add_uuid=True),
        get_template_study(add_uuid=True),
        get_template_image({"uuid": uuid.uuid4()}, add_uuid=True),
        get_template_file_reference({"uuid": uuid.uuid4()}, add_uuid=True),
        get_template_biosample(add_uuid=True),
        get_template_specimen({"uuid": uuid.uuid4()}, add_uuid=True),
        get_template_image_acquisition({"uuid": uuid.uuid4()}, add_uuid=True),
    ],
)
def test_context_creates_parseable_jsonld(
    rdf_graph: rdflib.Graph, json_object_dict: dict
):
    isParseable = False
    try:
        json_object_dict["@context"] = json.loads(
            urllib.request.urlopen(json_object_dict["@context"]).read().decode("utf-8")
        )

        rdf_graph.parse(data=json_object_dict, format="json-ld")
        isParseable = True
    except:
        isParseable = False

    assert isParseable
    assert len(rdf_graph) > 0
