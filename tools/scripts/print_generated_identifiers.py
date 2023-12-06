import uuid
import hashlib

import typer

app = typer.Typer()


def identifiers_for_file_and_image(accession_id: str, relative_path: str, size: int):
    """Generate UUIDs for both the FileReference and Image in an entry.
    
    The FileReference identifier is derived from the entry identifier, relative path
    to the file within the entry and file size.

    Image identifier is derived from the FileReference identifier.
    """

    hash_input = accession_id
    hash_input += str(relative_path)
    hash_input += str(size)
    hexdigest = hashlib.md5(hash_input.encode("utf-8")).hexdigest()

    fileref_id = str(uuid.UUID(version=4, hex=hexdigest))

    hash_input = fileref_id
    hexdigest = hashlib.md5(hash_input.encode("utf-8")).hexdigest()
    image_id_as_uuid = uuid.UUID(version=4, hex=hexdigest)
    image_id = str(image_id_as_uuid)

    return fileref_id, image_id


@app.command()
def print_file_and_image_identifiers(accession_id: str, relative_path: str, size: int):

    fileref_id, image_id = identifiers_for_file_and_image(accession_id, relative_path, size)
    print(f"{fileref_id},{image_id}")


    

if __name__ == "__main__":
    app()