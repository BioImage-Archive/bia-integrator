"""
! Maintain existing uuids to avoid breaking Embassy paths
"""

from bia_integrator_api import models as api_models, exceptions as api_exceptions
from bia_integrator_api.util import simple_client, PrivateApi
from src.bia_integrator_core import models as core_models, interface
import json

import uuid as uuid_lib
import time
import re
from urllib.request import urlopen
from urllib.error import HTTPError
from dataclasses import dataclass
from pathlib import Path

import typer
app = typer.Typer()

SCRIPT_DIR = Path(__file__).parent

@dataclass
class AppContext:
    """
    This is defined just for nice editor support
    """
    env_name: str
    config: dict
    api_client: PrivateApi

# Too big of a refactor to pass context everywhere, keep the (old) global variable for the client
api_client: PrivateApi = None

@app.callback()
def my_callback(
    ctx: typer.Context,
    env: str = typer.Option(default="dev"),
    config_path: Path = typer.Option(default=SCRIPT_DIR / "config.json", exists=True)
):
    with open(config_path, "r") as f:
        configs = json.load(f)

    if env not in configs:
        raise Exception(f"Unexpected environment {env}. Expecting one of: {','.join(configs.keys())} configured in {config_path}")

    config = configs[env]
    ctx.obj = AppContext(
        env_name=env,
        config=config,
        api_client=simple_client(
            config["biaint_api_url"],
            config["biaint_username"],
            config["biaint_password"],
            disable_ssl_host_check = True
        )
    )

    global api_client
    api_client = ctx.obj.api_client

studies_app = typer.Typer()
app.add_typer(studies_app, name="studies")

ome_metadata_app = typer.Typer()
app.add_typer(ome_metadata_app, name="ome")

class SkipStudyException(Exception):
    pass

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
    study_annotations_api = []
    for study_annotation_core in interface.get_study_annotations(study_core.accession_id):
        study_annotation_api = api_models.StudyAnnotation(
            author_email = getattr(study_annotation_core, "author_email", "migration@ebi.ac.uk"), 
            key = study_annotation_core.key,
            value = study_annotation_core.value,
            state = api_models.AnnotationState.ACTIVE
        )
        study_annotations_api.append(study_annotation_api)
    
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
        imaging_type = study_core.imaging_type,
        attributes = study_core.attributes.copy(),
        annotations = study_annotations_api,
        example_image_uri = study_core.example_image_uri,
        example_image_annotation_uri = study_core.example_annotation_uri, # different attribute name?
        tags = study_core.tags.copy()
    )

    return study

def file_reference_core_to_api(file_reference_core: core_models.FileReference, study_uuid, fileref_uuid = None):
    if not fileref_uuid:
        raise SkipStudyException("No fileref uuid")

    fileref_type = file_reference_core.type
    if fileref_type is None:
        if file_reference_core.uri.startswith("https://ftp.ebi.ac.uk"):
            fileref_type = "fire_object"
        elif file_reference_core.uri.endswith(".zarr.zip"):
            fileref_type = "zipped_zarr"
        else:
            fileref_type = "TODO - What do we do with null fileref types? Direct / in archive"
            #raise Exception("TODO - What do we do with null fileref types? Direct / in archive")
    
    fileref = api_models.FileReference(
        uuid = fileref_uuid,
        version = 0,
        study_uuid = study_uuid,
        name = file_reference_core.name,
        uri = file_reference_core.uri,
        type = fileref_type,
        size_in_bytes = file_reference_core.size_in_bytes,
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
        if file_uuid != bia_file_core.id and not re.match("https://www.ebi.ac.uk/biostudies/files.*", representation.uri):
            raise SkipStudyException("No file uuid and not a biostudies download link")

        fileref = api_models.FileReference(
            uuid = file_uuid,
            version = 0,
            study_uuid = study_uuid,
            name = bia_file_core.id,
            uri = representation.uri,
            type = file_type, #@TODO: Is this actually the type? 
            size_in_bytes = representation.size, # bytes?
            attributes = bia_file_core.attributes.copy()
        )
        filerefs.append(fileref)
    
    return filerefs

def representation_core_to_api(representation_core: core_models.BIAImageRepresentation, skip_study_if_on_embassy = False):
    file_in_biostudies = re.match("https://www.ebi.ac.uk/biostudies/files.*", str(representation_core.uri)) # if it's something other than str, it just won't match
    file_not_in_s3 = file_in_biostudies or representation_core.type in ["fire_object"]

    if skip_study_if_on_embassy and not file_not_in_s3 :
        print(representation_core)
        raise SkipStudyException(f"Image representation type {representation_core.type} not known to not have external dependencies")

    rendering = None
    if representation_core.rendering:
        channel_renders_api = [
            api_models.ChannelRendering(
                channel_label = None,
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

    return representation

def image_core_to_api(image_core: core_models.BIAImage, study_uuid, image_uuid = None, image_alias_core = None):
    if not image_uuid:
        # skipping is decided only from the representations / files associated with the image/study
        image_uuid = get_uuid()

    image_alias = None
    if image_alias_core:
        image_alias = api_models.BIAImageAlias(
            name = image_alias_core
        )

    image_representations = []
    for representation_core in image_core.representations:
        image_had_uuid = image_core.id == image_uuid
        representation_api = representation_core_to_api(representation_core, skip_study_if_on_embassy = not image_had_uuid)
        image_representations.append(representation_api)

    accession_id = image_core.accession_id if image_core.accession_id else image_core.representations[0].accession_id
    image_annotations_core = interface.get_image_annotations(accession_id, image_core.id)
    image_annotations = []
    for image_annotation_core in image_annotations_core:
        image_annotation = api_models.ImageAnnotation(
            author_email = getattr(image_annotation_core, "author_email", "migration@ebi.ac.uk"),
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

def image_set_ome_metadata_if_any(api_client: PrivateApi, study_image_api: api_models.BIAImage):
    """
    Mostly duplicated from scripts/fetch_ome_metadata_for_all_images_in_study.py,
        but tools isn't a dependency of the migration project
    After fully moving to prod, this should be deleted anyway
    """
    if not study_image_api.representations:
        return
    
    image_ome_ngff = [img_repr for img_repr in study_image_api.representations if img_repr.type == "ome_ngff"]
    if len(image_ome_ngff) == 0:
        # no ngff representation
        return
    elif len(image_ome_ngff) == 1:
        image_ome_ngff = image_ome_ngff.pop()
    else:
        # @TODO: Can we have this case? Adding to make it obvious when we do and decide then
        raise Exception(f"Image {study_image_api.uuid} has {len(image_ome_ngff)} ome_ngff representations. Which one to choose?")

    # Odd regex to at least make it invariant to url path, as long as it has a directory with .zarr somewhere
    #   e.g. sometimes urls end in myzarr.zarr, other times in myzarr.zarr/0
    # @TODO: Make this more robust? 
    ome_ngff_uri = re.sub(
        r"\.zarr.*",
        ".zarr/OME/METADATA.ome.xml",
        image_ome_ngff.uri[0]
    )
    print(f"Setting {ome_ngff_uri} as the ome xml of image {study_image_api.uuid}")

    ome_xml_basedir = Path("/tmp/ome_xml")
    ome_xml_basedir.mkdir(parents=True)

    ome_xml_file = ome_xml_basedir / ome_ngff_uri.replace("/","_")
    if not ome_xml_file.is_file():
        ome_metadata_contents = b""
        try:
            ome_metadata_contents = urlopen(ome_ngff_uri).read()
        except HTTPError as e:
            if e.status == 403:
                # TODO: What to do about this case? Does the ome xml really not exist?
                print(f"UNABLE TO FETCH {ome_ngff_uri} - SKIPPING")
                return

        if not len(ome_metadata_contents):
            print("Skipping empty ome xml")
            return
        ome_metadata_contents = str(ome_metadata_contents.decode())

        print(f"writing {len(ome_metadata_contents)} bytes to ome_metadata file {ome_xml_file}")
        with ome_xml_file.open() as f:
            f.write(ome_metadata_contents)

    api_client.set_image_ome_metadata(image_uuid=study_image_api.uuid, ome_metadata_file = str(ome_xml_file.resolve()))

def study_core_filerefs_to_api(study_core, study_api):
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
    
    return study_filerefs_api

def study_core_images_to_api(study_core, study_api):
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
    
    return study_images_api


def migrate_study(study_id):
    #study_core = study.get_study(study_id)
    study_core = interface.load_study_with_linked_objects_not_annotated(study_id)
    study_api = study_core_to_api(study_core)

    study_filerefs_api = study_core_filerefs_to_api(study_core=study_core, study_api=study_api)
    study_images_api = study_core_images_to_api(study_core=study_core, study_api=study_api)

    print(f"Creating study {study_id}")
    api_client.create_study(study_api)

    print(f"Creating {len(study_filerefs_api)} filerefs for study {study_id}")
    if len(study_filerefs_api):
        api_client.create_file_references(study_filerefs_api)

    print(f"Creating {len(study_images_api)} images for study {study_id}")
    if len(study_images_api):
        api_client.create_images(study_images_api)
    
    api_client.study_refresh_counts(study_api.uuid)

    print(f"DONE migrating study {study_id}\n")

@studies_app.command("migrate_one")
def migrate_one_study(study_accession: str):
    migrate_study(study_accession)

@studies_app.command("migrate_images_only")
def study_migrate_images_only(study_accession: str, bypass_duplication_check: bool = False):
    study_core = interface.load_study_with_linked_objects_not_annotated(study_accession)

    study_api = api_client.search_studies_exact_match(api_models.SearchStudyFilter(
        study_match = api_models.SearchStudy(
            accession_id = study_accession
        )
    ))[0]

    api_client.study_refresh_counts(study_api.uuid)
    study_api = api_client.get_study(study_api.uuid)
    if study_api.images_count and not bypass_duplication_check:
        raise Exception(f"Study already has {study_api.images_count} images. Stopping to avoid duplicating")

    study_images_api = study_core_images_to_api(study_core=study_core, study_api=study_api)

    print(f"Creating {len(study_images_api)} images for study {study_accession}")
    if len(study_images_api):
        api_client.create_images(study_images_api)

@studies_app.command("recount")
def study_refresh_counts(study_accession: str):
    study_api = api_client.search_studies_exact_match(api_models.SearchStudyFilter(
        study_match = api_models.SearchStudy(
            accession_id = study_accession
        )
    ))[0]

    api_client.study_refresh_counts(study_api.uuid)

@studies_app.command("migrate_all")
def migrate_all_studies():
    with open("skip.txt") as f:
        skip_accnos = set([l.strip() for l in f.readlines()])
    
    for study_id in interface.get_all_study_identifiers():
        if study_id.strip() in skip_accnos:
            # @TODO: NOT SURE skip this one because there is another study S-BIAD599 with the same accession
            continue

        print(f"Migrating study {study_id}")
        try:
            migrate_study(study_id)
        except SkipStudyException:
            print(f"Adding study {study_id} to skip list")
            skip_accnos.add(study_id)
            with open("skip.txt", "a") as f:
                f.writelines(skip_accnos)

@studies_app.command("collections_rebuild")
def rebuild_collection():
    data_dir = Path.home() / ".bia-integrator-data/collections"

    collection_files = data_dir.glob("**/*.json")
    collection_names = [collection_file.stem for collection_file in collection_files]
    for collection_name in collection_names:
        collection_exists = True
        try:
            api_client.search_collections(name=collection_name)
        except api_exceptions.NotFoundException:
            collection_exists = False

        if not collection_exists:
            collection_core = interface.get_collection(collection_name)
            
            collection_study_uuids = []
            for study_objinfo in api_client.get_object_info_by_accession(collection_core.accession_ids):
                collection_study_uuids.append(study_objinfo.uuid)
            
            collection_api = api_models.BIACollection(
                uuid = get_uuid(),
                version = 0,
                name=collection_name,
                title=collection_core.title,
                subtitle=collection_core.subtitle,
                description=collection_core.description,
                study_uuids=collection_study_uuids
            )
            api_client.create_collection(collection_api)

@studies_app.command("set_ome_xml_all")
def set_ome_xml_all():
    for study_api in api_client.search_studies(limit=1000000):
        for study_image in api_client.get_study_images(study_uuid=study_api.uuid, limit=1000000000):
            image_set_ome_metadata_if_any(api_client, study_image)

@studies_app.command("fix_annotated_studies")
def fix_annotated_studies():
    """
    For all studies that are both in the api and the data repo,
        goes through all annotations of the api study
        * if it would just be applied to attributes (not a field), deletes the attribute
        * if applying it (as a field) makes it mismatch the known-not-overwritten value in the data repo, throws so it can be fixed manually
            * ! "Unknown" values are just left overwritten
    """
    studies_in_api_only = []
    annotations_not_applied_in_api = []

    for api_study in api_client.search_studies(limit=1000000):
        b_any_changes = False
        b_in_data_repo = False

        if not api_study.annotations:
            continue

        try:
            data_repo_study = interface.load_study_with_linked_objects_not_annotated(api_study.accession_id)
            b_in_data_repo = True
        except FileNotFoundError as e:
            b_in_data_repo = False

        # Delete annotations that were applied as attributes
        for annotation in api_study.annotations:
            if annotation.key not in api_study.__dict__:
                b_any_changes = b_any_changes or api_study.attributes.pop(annotation.key, None)
            
            continue

        if b_in_data_repo:
            # go from api study annotations to data repo annotations and then copy back,
            #   to ensure there are no annotations that are only in the api (if there were, they would be handled separately)
            for annotation in api_study.annotations:
                if annotation.key in data_repo_study.__dict__:
                    if annotation.key not in api_study.__dict__:
                        # annotation not applied?
                        annotations_not_applied_in_api.append(annotation.key)
                        continue

                    if api_study.__dict__[annotation.key] != data_repo_study.__dict__[annotation.key]:
                        if data_repo_study.__dict__[annotation.key] in ["Unknown", ""]:
                            # these are ok to overwrite - leave them overwritten
                            continue

                        if annotation.key in ["example_image_uri"]:
                            # overwrite api attribute to the old data repo attribute
                            b_any_changes = True
                            api_study.__dict__[annotation.key] = data_repo_study.__dict__[annotation.key]
                        else:
                            raise Exception(f"{api_study.__dict__[annotation.key]} {data_repo_study.__dict__[annotation.key]}")
        
        #if b_any_changes:
        #    api_study.version += 1
        #    api_client.update_study(api_study)

if __name__ == "__main__":
    app()
