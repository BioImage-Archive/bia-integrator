from fastapi.testclient import TestClient


def test_fts(api_client: TestClient):
    rsp = api_client.get(
        f"/search/fts", params={"query": "ZFTA_RELA HEK293T Puncta Studies"}
    )
    assert rsp.status_code == 200

    body = rsp.json()
    assert body["total"]["value"] == 1


def test_get(api_client: TestClient):
    rsp = api_client.get(
        f"/website/doc", params={"uuid": "011cfb43-fa60-4e21-a047-e077c805840f"}
    )
    assert rsp.status_code == 200
