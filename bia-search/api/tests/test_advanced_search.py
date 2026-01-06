from fastapi.testclient import TestClient


def test_advanced_search_query(api_client: TestClient):
    rsp = api_client.get(
        f"/search/advanced",
        params={
            "query": "Homo sapiens",
        },
    )
    assert rsp.status_code == 200
    body = rsp.json()
    assert body["hits"]["total"]["value"] == 4


def test_advanced_search_facet_organism(api_client: TestClient):
    rsp = api_client.get(
        f"/search/advanced",
        params={"facet.organism": "Homo sapiens", "size_x.gt": "1024"},
    )
    assert rsp.status_code == 200
    body = rsp.json()
    assert body["hits"]["total"]["value"] == 1

    rsp = api_client.get(
        f"/search/advanced",
        params={
            "facet.organism.not": "Homo sapiens",
        },
    )
    assert rsp.status_code == 200
    body = rsp.json()
    assert body["hits"]["total"]["value"] == 4

    rsp = api_client.get(
        f"/search/advanced",
        params={
            "facet.organism.or": "Homo sapiens,Mus musculus",
        },
    )
    assert rsp.status_code == 200
    body = rsp.json()
    assert body["hits"]["total"]["value"] == 6


def test_advanced_search_image_attributes(api_client: TestClient):
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
        params={"query": "fluorescence microscopy", "size_y.lt": "1024"},
    )
    assert rsp.status_code == 200
    body = rsp.json()
    assert body["hits"]["total"]["value"] == 1

    rsp = api_client.get(
        f"/search/advanced",
        params={"facet.image_format": ".mcd"},
    )
    assert rsp.status_code == 200
    body = rsp.json()
    assert len(body["hits"]["hits"]) == 1


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
