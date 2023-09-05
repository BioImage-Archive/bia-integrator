"""
! Maintain existing uuids to avoid breaking Embassy paths
"""

from openapi_client import models as api_models
from openapi_client.util import simple_client
from bia_integrator_core import models as core_models, interface, study
import sys

import uuid as uuid_lib
import time
def get_uuid() -> str:
    # @TODO: make this constant and require mongo to always be clean?
    generated = uuid_lib.UUID(int=int(time.time()*1000000))

    return str(generated)

def is_uuid(maybe_uuid):
    try:
        uuid_lib.UUID(maybe_uuid)
        return True
    except ValueError:
        return False

def study_core_to_api(study_core: core_models.BIAStudy):
    study = api_models.BIAStudy(
        uuid = get_uuid(),
        version = 0,
        title = study_core.title,
        description = study_core.description,
        authors = [
            api_models.Author.from_json(author.json())
            for author in study_core.authors
        ],
        organism = study_core.organism,
        release_date = study_core.release_date,
        accession_id = study_core.accession_id,
        imaging_type = [study_core.imaging_type] if study_core.imaging_type else [],
        attributes = study_core.attributes.copy(),
        annotations = [], #todo
        example_image_uri = study_core.example_image_uri,
        example_image_annotation_uri = study_core.example_annotation_uri, # different attribute name?
        tags = study_core.tags.copy()
    )

    return study

def file_reference_core_to_api(file_reference_core: core_models.FileReference, study_uuid, fileref_uuid = None):
    if not fileref_uuid:
        fileref_uuid = get_uuid()
    
    fileref = api_models.FileReference(
        uuid = fileref_uuid,
        version = 0,
        study_uuid = study_uuid,
        name = file_reference_core.name,
        uri = file_reference_core.uri,
        type = file_reference_core.type if file_reference_core.type else "TODO - What do we do with null fileref types? Direct / in archive",
        size_bytes = file_reference_core.size_in_bytes,
        attributes = file_reference_core.attributes.copy()
    )

    return fileref

def bia_file_core_to_api(bia_file_core: core_models.BIAFile, study_uuid, file_uuid = None, file_type = None):
    if not file_uuid:
        file_uuid = get_uuid()
    
    # @TODO: representations deprecated (in models) - do we discard the data or fit it in FileReference?
    #   original_relpath ?
    filerefs = []
    for representation in bia_file_core.representations:
        fileref = api_models.FileReference(
            uuid = file_uuid,
            version = 0,
            study_uuid = study_uuid,
            name = bia_file_core.id,
            uri = representation.uri,
            type = file_type, #@TODO: Is this actually the type? 
            size_bytes = representation.size, # bytes?
            attributes = bia_file_core.attributes.copy()
        )
        filerefs.append(fileref)
    
    return filerefs

def image_core_to_api(image_core: core_models.BIAImage, study_uuid, image_uuid = None, image_alias_core = None, image_annotations_core = []):
    if not image_uuid:
        image_uuid = get_uuid()

    image_alias = None
    if image_alias_core:
        image_alias = api_models.BIAImageAlias(
            name = image_alias_core
        )

    image_representations = []
    for representation_core in image_core.representations:
        rendering = None
        if representation_core.rendering:
            channel_renders_api = [
                api_models.ChannelRendering(
                    colormap_start = channel_render_core.colormap_start,
                    colormap_end = channel_render_core.colormap_end,
                    scale_factor = channel_render_core.scale_factor
                )
                for channel_render_core in representation_core.rendering.channel_renders
            ]

            rendering = api_models.RenderingInfo(
                channel_renders = channel_renders_api,
                default_z = representation_core.rendering.default_z,
                default_t = representation_core.rendering.default_t
            )

        representation = api_models.BIAImageRepresentation(
            size = representation_core.size,
            uri = representation_core.uri if type(representation_core.uri) is list else [representation_core.uri],
            type = representation_core.type,
            dimensions = representation_core.dimensions,
            attributes = representation_core.attributes,
            rendering = rendering
        )
        image_representations.append(representation)

    image_annotations = []
    for image_annotation_core in image_annotations_core:
        image_annotation = api_models.ImageAnnotation(
            author_email = "TODO: Placeholder?", #@TODO
            key = image_annotation_core.key,
            value = image_annotation_core.value,
            state = api_models.AnnotationState.ACTIVE
        )
        image_annotations.append(image_annotation)

    image = api_models.BIAImage(
        uuid = image_uuid,
        version = 0,
        study_uuid = study_uuid,
        original_relpath = str(image_core.original_relpath),
        name = image_core.name,
        dimensions = image_core.dimensions,
        representations = image_representations,
        attributes = image_core.attributes.copy(),
        annotations = image_annotations,
        alias = image_alias
    )
    
    return image

def migrate_study(study_id):
    study_core = study.get_study(study_id)
    study_api = study_core_to_api(study_core)

    study_filerefs_api = []
    for k_fileref, fileref_core in study_core.file_references.items():
        fileref_uuid = k_fileref if is_uuid(k_fileref) else None

        fileref_api = file_reference_core_to_api(fileref_core, study_api.uuid, fileref_uuid)
        study_filerefs_api.append(fileref_api)
    
    for k_archive_file, archive_file_core in study_core.archive_files.items():
        archive_file_uuid = k_archive_file if is_uuid(k_archive_file) else None

        study_filerefs_api += bia_file_core_to_api(archive_file_core, study_api.uuid, archive_file_uuid, "archive")
    
    for k_other_file, other_file_core in study_core.other_files.items():
        other_file_uuid = k_other_file if is_uuid(k_other_file) else None

        study_filerefs_api += bia_file_core_to_api(other_file_core, study_api.uuid, other_file_uuid, "file")
    
    study_images_api = []
    for k_image, image_core in study_core.images.items():
        image_uuid = k_image if is_uuid(k_image) else None
        image_aliases = [
            alias.name
            for alias in study_core.image_aliases.values()
            if alias.image_id == k_image
        ]
        assert len(image_aliases) <= 1
        image_alias = image_aliases[0] if len(image_aliases) else None

        image_api = image_core_to_api(image_core, study_api.uuid, image_uuid, image_alias_core=image_alias)
        study_images_api.append(image_api)
    
    print(f"Creating study {study_id}")
    api_client.create_study(study_api)

    print(f"Creating {len(study_filerefs_api)} filerefs for study {study_id}")
    if len(study_filerefs_api):
        api_client.create_file_reference(study_filerefs_api)

    print(f"Creating {len(study_images_api)} images for study {study_id}")
    if len(study_images_api):
        api_client.create_images(study_images_api)

    print(f"DONE migrating study {study_id}\n")

config = {
    "biaint_api_url": "http://127.0.0.1:8080",
    "biaint_username": "test@example.com",
    "biaint_password": "test"
}

if __name__ == "__main__":
    api_client = simple_client(
        config["biaint_api_url"],
        config["biaint_username"],
        config["biaint_password"]
    )

    if len(sys.argv) >= 2:
        for study_id in sys.argv[1:]:
            migrate_study(study_id)
    else:
        print("Migrating all studies")
        for study_id in interface.get_all_study_identifiers():
            if study_id == "S-BIAD599_orig":
                # @TODO: NOT SURE skip this one because there is another study S-BIAD599 with the same accession
                continue

            print(f"Migrating study {study_id}")
            migrate_study(study_id)