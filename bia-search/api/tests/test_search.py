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


def test_fts_search_study_by_dataset_uuid(api_client: TestClient):
    dataset_uuid = "a227a231-b041-4d92-ae0f-4f72e3dca66c"
    rsp = api_client.get(f"/search/fts", params={"query": dataset_uuid})
    assert rsp.status_code == 200

    body = rsp.json()
    assert body["hits"]["total"]["value"] == 1

    dataset_uuids = [
        dataset["uuid"] for dataset in body["hits"]["hits"][0]["_source"]["dataset"]
    ]
    assert dataset_uuid in dataset_uuids


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
        f"/search/fts",
        params={"query": "with", "pagination.page": 1, "pagination.page_size": 1},
    )
    assert rsp.status_code == 200
    page_1 = rsp.json()
    assert len(page_1["hits"]["hits"]) == 1
    assert page_1["pagination"]["page"] == 1
    assert page_1["pagination"]["page_size"] == 1

    rsp = api_client.get(
        f"/search/fts",
        params={"query": "with", "pagination.page": 2, "pagination.page_size": 1},
    )
    assert rsp.status_code == 200
    page_2 = rsp.json()
    assert len(page_2["hits"]["hits"]) == 1
    assert page_2["pagination"]["page"] == 2
    assert page_2["pagination"]["page_size"] == 1

    rsp = api_client.get(
        f"/search/fts",
        params={"query": "with", "pagination.page": 1, "pagination.page_size": 2},
    )
    assert rsp.status_code == 200
    pages_both = rsp.json()
    assert len(pages_both["hits"]["hits"]) == 2
    uuids_in_both = [hit["_source"]["uuid"] for hit in pages_both["hits"]["hits"]]
    uuid_1 = page_1["hits"]["hits"][0]["_source"]["uuid"]
    uuid_2 = page_2["hits"]["hits"][0]["_source"]["uuid"]
    assert [uuid_1, uuid_2] == uuids_in_both


def test_fts_image_facet_discovery_organism(api_client: TestClient):
    rsp = api_client.get(f"/search/fts/image", params={"query": "Homo sapiens"})
    assert rsp.status_code == 200

    body = rsp.json()
    assert len(body["facets"]["scientific_name"]["buckets"]) == 1
    assert {
        "key": "Homo sapiens",
        "doc_count": 2,
    } in body["facets"][
        "scientific_name"
    ]["buckets"]


def test_fts_image_facet_discovery_imaging_method(api_client: TestClient):
    rsp = api_client.get(
        f"/search/fts/image", params={"query": "fluorescence microscopy"}
    )
    assert rsp.status_code == 200

    body = rsp.json()
    assert len(body["facets"]["imaging_method"]["buckets"]) == 1


def test_fts_image_no_query(api_client: TestClient):
    rsp = api_client.get(f"/search/fts/image")
    assert rsp.status_code == 200
    body = rsp.json()
    facet_homo_sapiens = next(
        bucket
        for bucket in body["facets"]["scientific_name"]["buckets"]
        if bucket["key"] == "Homo sapiens"
    )["doc_count"]
    assert len(body["hits"]["hits"]) == 3

    rsp = api_client.get(
        f"/search/fts/image", params={"facet.organism": ["Homo sapiens"]}
    )
    assert rsp.status_code == 200
    body = rsp.json()
    assert len(body["hits"]["hits"]) == facet_homo_sapiens


def test_fts_image_use_facet_imaging_method(api_client: TestClient):
    rsp = api_client.get(
        f"/search/fts/image",
        params={
            "facet.imaging_method": ["confocal microscopy", "fluorescence microscopy"]
        },
    )
    assert rsp.status_code == 200
    body = rsp.json()
    assert len(body["hits"]["hits"]) == 2


def test_fts_image_paging(api_client: TestClient):
    rsp = api_client.get(
        f"/search/fts/image",
        params={"query": "", "pagination.page": 1, "pagination.page_size": 1},
    )
    assert rsp.status_code == 200
    page_1 = rsp.json()
    assert len(page_1["hits"]["hits"]) == 1
    assert page_1["pagination"]["page"] == 1
    assert page_1["pagination"]["page_size"] == 1

    rsp = api_client.get(
        f"/search/fts/image",
        params={"query": "", "pagination.page": 2, "pagination.page_size": 1},
    )
    assert rsp.status_code == 200
    page_2 = rsp.json()
    assert len(page_2["hits"]["hits"]) == 1
    assert page_2["pagination"]["page"] == 2
    assert page_2["pagination"]["page_size"] == 1

    rsp = api_client.get(
        f"/search/fts/image",
        params={"query": "", "pagination.page": 1, "pagination.page_size": 2},
    )
    assert rsp.status_code == 200
    pages_both = rsp.json()
    assert len(pages_both["hits"]["hits"]) == 2
    uuids_in_both = [hit["_source"]["uuid"] for hit in pages_both["hits"]["hits"]]
    uuid_1 = page_1["hits"]["hits"][0]["_source"]["uuid"]
    uuid_2 = page_2["hits"]["hits"][0]["_source"]["uuid"]
    assert [uuid_1, uuid_2] == uuids_in_both


def test_fts_image_derived_images(api_client: TestClient):
    rsp = api_client.get(
        f"/search/fts/image",
        params={
            "query": "0931a00e-d4dc-4c82-9809-4fdeffb1fc2e",
            "includeDerivedImages": "true",
        },
    )
    assert rsp.status_code == 200

    body = rsp.json()
    assert body["hits"]["total"]["value"] == 2
    assert (
        body["hits"]["hits"][0]["_source"]["uuid"]
        == "0931a00e-d4dc-4c82-9809-4fdeffb1fc2e"
    )
    assert (
        body["hits"]["hits"][1]["_source"]["uuid"]
        == "2b3c7b46-c31f-4b0a-ac1b-29c2dee8eebf"
    )


def test_fts_image_imagerep_dimensions(api_client: TestClient):
    rsp = api_client.get(
        f"/search/fts/image",
        params={
            "size_x.gt": "1024",
            "size_y.gt": "1024",
        },
    )
    assert rsp.status_code == 200
    body = rsp.json()
    assert body["hits"]["total"]["value"] == 1

    rsp = api_client.get(
        f"/search/fts/image",
        params={
            "size_c.lt": "2",
        },
    )
    assert rsp.status_code == 200
    body = rsp.json()
    assert body["hits"]["total"]["value"] == 2

    rsp = api_client.get(
        f"/search/fts/image",
        params={
            "total_size_in_bytes.gt": "2000000",
        },
    )
    assert rsp.status_code == 200
    body = rsp.json()
    assert body["hits"]["total"]["value"] == 1


def test_advanced_search(api_client: TestClient):
    rsp = api_client.get(
        f"/search/advanced",
        params={
            "size_c.lt": "2",
        },
    )
    assert rsp.status_code == 200
    body = rsp.json()
    assert body["hits"]["total"]["value"] == 2

    rsp = api_client.get(
        f"/search/advanced",
        params={
            "query": "Homo sapiens",
        },
    )
    assert rsp.status_code == 200
    body = rsp.json()
    assert body["hits"]["total"]["value"] == 4

    rsp = api_client.get(
        f"/search/advanced",
        params={"facet.organism": "Homo sapiens", "size_x.gt": "1024"},
    )
    assert rsp.status_code == 200
    body = rsp.json()
    assert body["hits"]["total"]["value"] == 1

    rsp = api_client.get(
        f"/search/advanced",
        params={"query": "fluorescence microscopy", "size_x.gt": "1024"},
    )
    assert rsp.status_code == 200
    body = rsp.json()
    assert body["hits"]["total"]["value"] == 2


def test_advanced_search_paging(api_client: TestClient):
    rsp = api_client.get(
        f"/search/advanced",
        params={"query": "", "pagination.page": 1, "pagination.page_size": 1},
    )
    assert rsp.status_code == 200
    page_1 = rsp.json()
    assert len(page_1["hits"]["hits"]) == 1
    assert page_1["pagination"]["page"] == 1
    assert page_1["pagination"]["page_size"] == 1

    rsp = api_client.get(
        f"/search/advanced",
        params={"query": "", "pagination.page": 2, "pagination.page_size": 1},
    )
    assert rsp.status_code == 200
    page_2 = rsp.json()
    assert len(page_2["hits"]["hits"]) == 1
    assert page_2["pagination"]["page"] == 2
    assert page_2["pagination"]["page_size"] == 1

    rsp = api_client.get(
        f"/search/advanced",
        params={"query": "", "pagination.page": 1, "pagination.page_size": 2},
    )
    assert rsp.status_code == 200
    pages_both = rsp.json()
    assert len(pages_both["hits"]["hits"]) == 2
    uuids_in_both = [hit["_source"]["uuid"] for hit in pages_both["hits"]["hits"]]
    uuid_1 = page_1["hits"]["hits"][0]["_source"]["uuid"]
    uuid_2 = page_2["hits"]["hits"][0]["_source"]["uuid"]
    assert [uuid_1, uuid_2] == uuids_in_both
