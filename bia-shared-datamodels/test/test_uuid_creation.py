from bia_shared_datamodels import uuid_creation
from uuid import uuid4

def test_uuid_and_string_has_same_result():
    test_uuid = uuid4()
    test_uuid_str = str(test_uuid)
    assert uuid_creation.__list_to_uuid([test_uuid]) == uuid_creation.__list_to_uuid(
        [test_uuid_str]
    )

    title = "test title"
    assert uuid_creation.create_dataset_uuid(title, test_uuid) == uuid_creation.create_dataset_uuid(title, test_uuid_str)
