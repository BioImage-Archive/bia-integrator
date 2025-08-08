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
        "doc_count": 2,
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
        "doc_count": 3,
    } in body["facets"][
        "scientific_name"
    ]["buckets"]


def test_fts_facet_discovery_release_date(api_client: TestClient):
    rsp = api_client.get(f"/search/fts", params={"query": "with"})
    assert rsp.status_code == 200

    body = rsp.json()
    assert {"key_as_string": "2024", "key": 1704067200000, "doc_count": 2} in body[
        "facets"
    ]["release_date"]["buckets"]
    assert {"key_as_string": "2025", "key": 1735689600000, "doc_count": 3} in body[
        "facets"
    ]["release_date"]["buckets"]


def test_fts_facet_discovery_imaging_method(api_client: TestClient):
    rsp = api_client.get(f"/search/fts", params={"query": "with"})
    assert rsp.status_code == 200

    body = rsp.json()
    assert len(body["facets"]["imaging_method"]["buckets"]) == 2


def test_fts_use_facet_organism(api_client: TestClient):
    rsp = api_client.get(
        f"/search/fts",
        params={"query": "with", "organism": ["Homo sapiens", "Mus musculus"]},
    )
    assert rsp.status_code == 200

    body = rsp.json()
    assert len(body["hits"]["hits"]) == 4


def test_fts_use_facet_year(api_client: TestClient):
    rsp = api_client.get(
        f"/search/fts",
        params={"query": "with", "year": ["2024"]},
    )
    assert rsp.status_code == 200
    body = rsp.json()
    assert len(body["hits"]["hits"]) == 2


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


def test_search_with_filter_restricts_results(api_client: TestClient):
    rsp_all = api_client.get(
        f"/search/fts",
        params={"query": "with"},
    )
    assert rsp_all.status_code == 200
    body_all = rsp_all.json()
    assert len(body_all["hits"]["hits"]) == 5
    assert body_all["hits"]["total"]["value"] == len(body_all["hits"]["hits"])

    expected_filtered_count = [
        i["doc_count"]
        for i in body_all["facets"]["scientific_name"]["buckets"]
        if i["key"] == "Homo sapiens"
    ][0]
    rsp_filtered = api_client.get(
        f"/search/fts",
        params={"query": "with", "organism": ["Homo sapiens"]},
    )
    assert rsp_filtered.status_code == 200
    body_filtered = rsp_filtered.json()
    assert len(body_filtered["hits"]["hits"]) == expected_filtered_count
    assert body_filtered["hits"]["total"]["value"] == len(body_filtered["hits"]["hits"])

    all_uuids = set(hit["_source"]["uuid"] for hit in body_all["hits"]["hits"])
    filtered_uuids = set(
        hit["_source"]["uuid"] for hit in body_filtered["hits"]["hits"]
    )
    assert filtered_uuids.issubset(filtered_uuids), filtered_uuids.symmetric_difference(
        all_uuids
    )
