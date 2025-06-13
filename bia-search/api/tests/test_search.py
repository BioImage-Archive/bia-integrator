from fastapi.testclient import TestClient


def test_fts(api_client: TestClient):
    rsp = api_client.get(f"/fts", params={"query": "ZFTA_RELA HEK293T Puncta Studies"})
    assert rsp.status_code == 200

    body = rsp.json()
    assert body["total"]["value"] == 1
