import uuid
import hashlib

from .biostudies import File


def file_to_id(accession_id: str, file: File):

    hash_input = accession_id
    hash_input += str(file.path)
    hash_input += str(file.size)
    hexdigest = hashlib.md5(hash_input.encode("utf-8")).hexdigest()

    id_as_uuid = uuid.UUID(version=4, hex=hexdigest)

    return str(id_as_uuid)


def test_bst_file_to_uuid():

    first_bst_file = File(path="file1.tif", size=123)
    second_bst_file = File(path="file2.tif", size=456)
    third_bst_file = File(path="file2.tif", size=789)

    # id is a string
    id = file_to_id(accession_id="foo1", file=first_bst_file)
    assert isinstance(id, str)

    # Same accession, same file, same size should produce same id
    first_id = file_to_id(accession_id="foo1", file=first_bst_file)
    second_id = file_to_id(accession_id="foo1", file=first_bst_file)
    assert first_id == second_id

    # Same accession, different filename should produce different ids
    first_id = file_to_id(accession_id="foo1", file=first_bst_file)
    second_id = file_to_id(accession_id="foo1", file=second_bst_file)
    assert first_id != second_id

    # Different accession, same filename should produce different ids
    first_id = file_to_id(accession_id="foo1", file=first_bst_file)
    second_id = file_to_id(accession_id="foo2", file=first_bst_file)
    assert first_id != second_id

    # Same accession, same filename, different size should produce different ids
    first_id = file_to_id(accession_id="foo1", file=second_bst_file)
    second_id = file_to_id(accession_id="foo1", file=third_bst_file)
    assert first_id != second_id