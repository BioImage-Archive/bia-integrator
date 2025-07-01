from fastapi.testclient import TestClient


def test_fts(api_client: TestClient):
    rsp = api_client.get(
        f"/search/fts", params={"query": "ZFTA_RELA HEK293T Puncta Studies"}
    )
    assert rsp.status_code == 200

    body = rsp.json()
    assert body["total"]["value"] == 1


def test_get(api_client: TestClient):
    doc_uuid = "87089e93-1775-45b9-8695-190630681c3b"
    rsp = api_client.get(f"/website/doc", params={"uuid": doc_uuid})
    assert rsp.status_code == 200

    body = rsp.json()
    assert len(body["hits"]) == 1
    assert body["hits"][0]["_source"]["uuid"] == doc_uuid
