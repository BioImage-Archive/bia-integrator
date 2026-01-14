from fastapi.testclient import TestClient


def test_fts_image_facet_discovery_organism(api_client: TestClient):
    rsp = api_client.get(f"/search/fts/image", params={"query": "Homo sapiens"})
    assert rsp.status_code == 200

    body = rsp.json()
    assert len(body["facets"]["scientific_name"]["buckets"]) == 1
    assert {
        "key": "homo sapiens",
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
        if bucket["key"] == "homo sapiens"
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
            "facet.imaging_method": [
                "confocal microscopy",
                "fluorescence microscopy",
            ]
        },
    )
    assert rsp.status_code == 200
    body = rsp.json()
    assert len(body["hits"]["hits"]) == 2


def test_fts_image_use_facet_image_format(api_client: TestClient):
    rsp = api_client.get(
        f"/search/fts/image",
        params={"facet.image_format.eq": ".mcd"},
    )
    assert rsp.status_code == 200
    body = rsp.json()
    assert len(body["hits"]["hits"]) == 1


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
