from uuid import uuid4, UUID
from copy import deepcopy
from bia_shared_datamodels import bia_data_model, uuid_creation, semantic_models
from bia_test_data.mock_objects import mock_file_reference
from bia_test_data.mock_objects.utils import accession_id


file_uri_base = "https://uk1s3.embassy.ebi.ac.uk/bia-integrator-data"
# We are using image im06.png from study component 2
file_reference = mock_file_reference.get_file_reference(["biad_v4/file_list_study_component_2.json"])[0]
image_uuid = uuid_creation.create_image_uuid([file_reference.uuid,])
representation_dict_template= {
        "image_format": "",
        # "use_type": to be added by template user,
        # "file_uri": to be added by template user,
        "representation_of_uuid": image_uuid,
        "total_size_in_bytes": 0, # overwrite by template user if necessary
        # "physical_size_x": 0,
        # "physical_size_y": 0,
        # "physical_size_z": 0,
        "size_x": None, # overwrite by template user if necessary
        "size_y": None, # overwrite by template user if necessary
        "size_z": None, # overwrite by template user if necessary
        "size_c": None, # overwrite by template user if necessary
        "size_t": None, # overwrite by template user if necessary
        "version": 0,
    }

def get_image_representation_of_uploaded_by_submitter() -> bia_data_model.ImageRepresentation:
    
    representation_dict = deepcopy(representation_dict_template)
    representation_dict["use_type"] = semantic_models.ImageRepresentationUseType.UPLOADED_BY_SUBMITTER
    representation_dict["image_format"] = ".png"
    representation_dict["file_uri"] = [file_reference.uri,]
    representation_dict["total_size_in_bytes"] = file_reference.size_in_bytes
    representation_dict["uuid"] = uuid_creation.create_image_representation_uuid(
        image_uuid,
        representation_dict["image_format"],
        representation_dict["use_type"],
    )
    return bia_data_model.ImageRepresentation.model_validate(representation_dict)

def get_image_representation_of_thumbnail() -> bia_data_model.ImageRepresentation:
    
    representation_dict = deepcopy(representation_dict_template)
    representation_dict["use_type"] = semantic_models.ImageRepresentationUseType.THUMBNAIL
    representation_dict["image_format"] = ".png"
    # TODO: create actual image and get the size
    #       However, on initial creation of representation we would not
    #       normally know this - except if we already have the thumbnail
    #representation_dict["total_size_in_bytes"] = 
    image_representation_uuid = uuid_creation.create_image_representation_uuid(
        image_uuid,
        representation_dict["image_format"],
        representation_dict["use_type"],
    )
    representation_dict["uuid"] = image_representation_uuid
    file_uri = f"{file_uri_base}/{accession_id}/{image_uuid}/{image_representation_uuid}.png"
    representation_dict["file_uri"] = [file_uri,]
    return bia_data_model.ImageRepresentation.model_validate(representation_dict)

def get_image_representation_of_static_display() -> bia_data_model.ImageRepresentation:
     
    representation_dict = deepcopy(representation_dict_template)
    representation_dict["use_type"] = semantic_models.ImageRepresentationUseType.STATIC_DISPLAY
    representation_dict["image_format"] = ".png"
    # TODO: create actual image and get the size
    #representation_dict["total_size_in_bytes"] = 
    image_representation_uuid = uuid_creation.create_image_representation_uuid(
        image_uuid,
        representation_dict["image_format"],
        representation_dict["use_type"],
    )
    representation_dict["uuid"] = image_representation_uuid
    file_uri = f"{file_uri_base}/{accession_id}/{image_uuid}/{image_representation_uuid}.png"
    representation_dict["file_uri"] = [file_uri,]
    return bia_data_model.ImageRepresentation.model_validate(representation_dict)

def get_image_representation_of_interactive_display() -> bia_data_model.ImageRepresentation:
     
    representation_dict = deepcopy(representation_dict_template)
    representation_dict["use_type"] = semantic_models.ImageRepresentationUseType.INTERACTIVE_DISPLAY
    representation_dict["image_format"] = ".ome.zarr"
    # TODO: create actual image and get the size
    #representation_dict["total_size_in_bytes"] = 
    image_representation_uuid = uuid_creation.create_image_representation_uuid(
        image_uuid,
        representation_dict["image_format"],
        representation_dict["use_type"],
    )
    representation_dict["uuid"] = image_representation_uuid
    file_uri = f"{file_uri_base}/{accession_id}/{image_uuid}/{image_representation_uuid}.ome.zarr"
    representation_dict["file_uri"] = [file_uri,]
    return bia_data_model.ImageRepresentation.model_validate(representation_dict)

