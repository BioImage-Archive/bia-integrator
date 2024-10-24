# Note: This file is all commented out because the feature, which enabled us
# to define union types for connections in the api, is not currently being used
# by any API endpoints, therefore there is not valid endpoint to test.

# from api.tests.conftest import get_uuid


# from fastapi.testclient import TestClient


# def test_known_bug_should_not_pass_but_does_union_reference_typed_lists_not_exclusive(
#     api_client: TestClient,
#     existing_annotaton_file_reference: dict,
#     existing_derived_image: dict,
#     existing_image: dict,
# ):
#     existing_annotaton_file_reference |= {
#         "uuid": get_uuid(),
#         "source_image_uuid": [
#             # this should cause an error, because the source images aren't of the same type
#             existing_derived_image["uuid"],
#             existing_image["uuid"],
#         ],
#     }
#     rsp = api_client.post(
#         "private/annotation_file_reference",
#         json=existing_annotaton_file_reference,
#     )
#     assert rsp.status_code == 201, "Fixed the bug!"


# def test_cannot_resolve_reverse_union_link_from_mistyped_parent(
#     api_client: TestClient,
#     existing_annotaton_file_reference: dict,
#     existing_image: dict,
# ):
#     existing_annotaton_file_reference |= {
#         "uuid": get_uuid(),
#         "source_image_uuid": [
#             # Note no derived_image anywhere
#             existing_image["uuid"],
#         ],
#     }
#     rsp = api_client.post(
#         "private/annotation_file_reference",
#         json=existing_annotaton_file_reference,
#     )
#     assert rsp.status_code == 201

#     rsp = api_client.get(
#         # existing_experimentally_captured_image exists but is not a derived_image
#         f"derived_image/{existing_image['uuid']}/annotation_file_reference",
#         params={"page_size": 100},
#     )
#     assert rsp.status_code == 404
