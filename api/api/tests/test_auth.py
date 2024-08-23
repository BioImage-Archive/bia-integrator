from fastapi.testclient import TestClient
from api.tests.conftest import get_uuid


def test_authenticate_user(api_client_public: TestClient, existing_user: dict):
    rsp = api_client_public.post("auth/token", data=existing_user)

    assert rsp.status_code == 200
    assert list(rsp.json().keys()) == ["access_token", "token_type"]


def test_authenticate_missing_user(api_client_public: TestClient, existing_user: dict):
    new_user = existing_user.copy()

    new_user["username"] = "this_user_does_not_exist"
    rsp = api_client_public.post("auth/token", data=new_user)

    assert rsp.status_code == 401
    assert rsp.json() == {
        "detail": "Incorrect username or password"
    }, "More/different info than expected provided at login failure"


def test_authenticate_bad_password(api_client_public: TestClient, existing_user: dict):
    new_user = existing_user.copy()

    new_user["password"] = "badpass"
    rsp = api_client_public.post("auth/token", data=new_user)

    assert rsp.status_code == 401
    assert rsp.json() == {
        "detail": "Incorrect username or password"
    }, "More/different info than expected provided at login failure"


def test_unauthenticated_get_accepted(
    api_client_public: TestClient, existing_study: dict
):
    rsp = api_client_public.get(f"study/{existing_study['uuid']}")
    assert rsp.status_code == 200
    assert rsp.json() == existing_study


def test_unauthenticated_bad_token_get_accepted(
    api_client_public: TestClient, existing_study: dict
):
    # get requests don't check authorization headers at all
    rsp = api_client_public.get(
        f"study/{existing_study['uuid']}", headers={"Authorization": "1234"}
    )
    assert rsp.status_code == 200
    assert rsp.json() == existing_study


def test_unauthenticated_bad_token_post_rejected(
    api_client_public: TestClient, existing_study: dict
):
    existing_study["uuid"] = get_uuid()

    rsp = api_client_public.post("private/study", headers={"Authorization": "1234"})
    assert rsp.status_code == 401, rsp.json()
    assert rsp.json() == {
        "detail": "Not authenticated"
    }, "More/different info than expected provided when attempting to access a private resource"


def test_unauthenticated_create_rejected(
    api_client_public: TestClient, existing_study: dict
):
    existing_study["uuid"] = get_uuid()

    rsp = api_client_public.post("private/study", json=existing_study)
    assert rsp.status_code == 401, rsp.json()
    assert rsp.json() == {
        "detail": "Not authenticated"
    }, "More/different info than expected provided when attempting to access a private resource"


def test_create_user(api_client_public: TestClient, user_create_token: str, uuid: str):
    post_data = {
        "email": f"test_{uuid}@test.com",
        "password_plain": uuid,
        "secret_token": user_create_token,
    }

    rsp = api_client_public.post("auth/user/register", json=post_data)
    assert rsp.status_code == 200


def test_create_user_bad_token(api_client_public: TestClient, uuid: str):
    post_data = {
        "email": f"test_{uuid}@test.com",
        "password_plain": uuid,
        "secret_token": "2345==",
    }

    rsp = api_client_public.post("auth/user/register", json=post_data)
    assert rsp.status_code == 401, rsp.json()
    assert rsp.json() == {"detail": "Unauthorized"}
