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
        # Passing in UUID in dicitionary as we don't need a study from the test db & Pytest's parametrised tests use fixture values
        # rather than the function (see https://github.com/pytest-dev/pytest/issues/349). We could use https://github.com/tvorog/pytest-lazy-fixture
        # if we need this feature.
        get_template_image(existing_study={"uuid": uuid.uuid4()}, add_uuid=True),
        get_template_file_reference(
            existing_study={"uuid": uuid.uuid4()}, add_uuid=True
        ),
        get_template_biosample(add_uuid=True),
        get_template_specimen(existing_biosample={"uuid": uuid.uuid4()}, add_uuid=True),
        get_template_image_acquisition(
            existing_specimen={"uuid": uuid.uuid4()}, add_uuid=True
        ),
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
