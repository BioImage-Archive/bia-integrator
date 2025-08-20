from fastapi.testclient import TestClient


def test_fts(api_client: TestClient):
    rsp = api_client.get(
        f"/search/fts", params={"query": "ZFTA_RELA HEK293T Puncta Studies"}
    )
    assert rsp.status_code == 200

    body = rsp.json()
    assert body["hits"]["total"]["value"] == 1


def test_fts_facet_discovery_organism(api_client: TestClient):
    rsp = api_client.get(f"/search/fts", params={"query": "with"})
    assert rsp.status_code == 200

    body = rsp.json()
    assert len(body["facets"]["scientific_name"]["buckets"]) == 3
    assert {
        "key": "Homo sapiens",
        "doc_count": 1,
    } in body["facets"][
        "scientific_name"
    ]["buckets"]
    assert {
        "key": "Drosophila melanogaster",
        "doc_count": 1,
    } in body["facets"][
        "scientific_name"
    ]["buckets"]
    assert {
        "key": "Mus musculus",
        "doc_count": 2,
    } in body["facets"][
        "scientific_name"
    ]["buckets"]


def test_fts_facet_discovery_release_date(api_client: TestClient):
    rsp = api_client.get(f"/search/fts", params={"query": "with"})
    assert rsp.status_code == 200

    body = rsp.json()
    assert {"key_as_string": "2024", "key": 1704067200000, "doc_count": 1} in body[
        "facets"
    ]["release_date"]["buckets"]
    assert {"key_as_string": "2025", "key": 1735689600000, "doc_count": 3} in body[
        "facets"
    ]["release_date"]["buckets"]


def test_fts_facet_discovery_imaging_method(api_client: TestClient):
    rsp = api_client.get(f"/search/fts", params={"query": "with"})
    assert rsp.status_code == 200

    body = rsp.json()
    assert len(body["facets"]["imaging_method"]["buckets"]) == 1


def test_fts_use_facet_organism(api_client: TestClient):
    rsp = api_client.get(
        f"/search/fts",
        params={"query": "with", "facet.organism": ["Homo sapiens", "Mus musculus"]},
    )
    assert rsp.status_code == 200

    body = rsp.json()
    assert len(body["hits"]["hits"]) == 3


def test_fts_no_query(api_client: TestClient):
    rsp = api_client.get(f"/search/fts")
    assert rsp.status_code == 200
    body = rsp.json()
    facet_homo_sapiens = next(
        bucket
        for bucket in body["facets"]["scientific_name"]["buckets"]
        if bucket["key"] == "Homo sapiens"
    )["doc_count"]
    assert len(body["hits"]["hits"]) == 5

    rsp = api_client.get(f"/search/fts", params={"facet.organism": ["Homo sapiens"]})
    assert rsp.status_code == 200
    body = rsp.json()
    assert len(body["hits"]["hits"]) == facet_homo_sapiens


def test_fts_use_facet_year(api_client: TestClient):
    rsp = api_client.get(
        f"/search/fts",
        params={"query": "with", "facet.year": ["2024"]},
    )
    assert rsp.status_code == 200
    body = rsp.json()
    assert len(body["hits"]["hits"]) == 1


def test_fts_use_facet_imaging_method(api_client: TestClient):

    rsp = api_client.get(
        f"/search/fts",
        params={"query": "with", "imaging_method": ["confocal microscopy"]},
    )
    assert rsp.status_code == 200
    body = rsp.json()
    assert len(body["hits"]["hits"]) == 4


def test_get(api_client: TestClient):
    doc_uuid = "87089e93-1775-45b9-8695-190630681c3b"
    rsp = api_client.get(f"/website/doc", params={"uuid": doc_uuid})
    assert rsp.status_code == 200

    body = rsp.json()
    assert len(body["hits"]) == 1
    assert body["hits"][0]["_source"]["uuid"] == doc_uuid


def test_fts_image(api_client: TestClient):
    rsp = api_client.get(
        f"/search/fts/image", params={"query": "445cb17b-95dc-47a3-9efc-b7a1a066bb51"}
    )
    assert rsp.status_code == 200

    body = rsp.json()
    assert body["hits"]["total"]["value"] == 1
    assert (
        body["hits"]["hits"][0]["_source"]["uuid"]
        == "445cb17b-95dc-47a3-9efc-b7a1a066bb51"
    )


def test_fts_paging(api_client: TestClient):
    rsp = api_client.get(
        f"/search/fts", params={"query": "with", "page": 1, "page_size": 1}
    )
    assert rsp.status_code == 200
    body = rsp.json()
    assert len(body["hits"]["hits"]) == 1
    assert body["pagination"]["page"] == 1
    assert body["pagination"]["page_size"] == 1

    rsp = api_client.get(
        f"/search/fts", params={"query": "with", "page": 2, "page_size": 1}
    )
    assert rsp.status_code == 200
    body = rsp.json()
    assert len(body["hits"]["hits"]) == 1
    assert body["pagination"]["page"] == 2
    assert body["pagination"]["page_size"] == 1
