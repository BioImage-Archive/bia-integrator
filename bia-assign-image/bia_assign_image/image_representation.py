from uuid import UUID
from pathlib import Path
from typing import List
from bia_shared_datamodels import bia_data_model, semantic_models, uuid_creation

def get_image_representation(
        accession_id: str,
        file_references: List[bia_data_model.FileReference,],
        image_uuid: UUID,
        use_type: semantic_models.ImageRepresentationUseType,
        # TODO: Decide whether to let user specify image format - 
        #       ATM we use uploaded_by_submitter is decided by suffix
        #       thumbnail and statid display are png
        #       interactive display is ome.zarr
        #image_format: Optional[str | None] = None,
    ) -> bia_data_model.ImageRepresentation:
    
    # TODO: Put this is settings
    file_uri_base = "https://uk1s3.embassy.ebi.ac.uk/bia-integrator-data"
    
    # TODO: Is it OK to assume image_uuid is correct or should we check
    #       file references in image_uuid match those in image representation?

    if not isinstance(use_type, semantic_models.ImageRepresentationUseType):
        use_type = semantic_models.ImageRepresentationUseType(use_type.upper())

    total_size_in_bytes = 0 
    if use_type == semantic_models.ImageRepresentationUseType.UPLOADED_BY_SUBMITTER:
        assert len(file_references) == 1
        
        #if image_format is not None:
        #    assert image_format.endswith(file_reference_ext)
        #else:
        #    image_format = get_image_extension(file_references[0].file_path)
        
        image_format = get_image_extension(file_references[0].file_path)
        total_size_in_bytes = file_references[0].size_in_bytes
    else:
        image_format_map = {
            semantic_models.ImageRepresentationUseType.THUMBNAIL: ".png",
            semantic_models.ImageRepresentationUseType.STATIC_DISPLAY: ".png",
            semantic_models.ImageRepresentationUseType.INTERACTIVE_DISPLAY: ".ome.zarr",
        }
        image_format = image_format_map[use_type]
    
    image_representation_uuid = uuid_creation.create_image_representation_uuid(
        image_uuid,
        image_format,
        use_type,
    )

    if use_type == semantic_models.ImageRepresentationUseType.UPLOADED_BY_SUBMITTER:
        file_uri = file_references[0].uri
    else:
        file_uri = f"{file_uri_base}/{accession_id}/{image_uuid}/{image_representation_uuid}{image_format}"

    model_dict = {
        "uuid": image_representation_uuid,
        "version": 0,
        "use_type": use_type,
        "representation_of_uuid": image_uuid,
        "file_uri": [file_uri,],
        "total_size_in_bytes": total_size_in_bytes,
        "image_format": image_format,
    }
    
    return bia_data_model.ImageRepresentation.model_validate(model_dict)

# Copied from bia_converter_light.utils 
def get_image_extension(file_path: str) -> str:
    """Return standardized image extension for a given file path."""

    # Process files with multi suffix extensions
    multi_suffix_ext = {
        ".ome.zarr.zip": ".ome.zarr.zip",
        ".zarr.zip": ".zarr.zip",
        ".ome.zarr": ".ome.zarr",
        ".ome.tiff": ".ome.tiff",
        ".ome.tif": ".ome.tiff",
        ".tar.gz": ".tar.gz",
    }

    for ext, mapped_value in multi_suffix_ext.items():
        if file_path.lower().endswith(ext):
            return mapped_value

    # Standardise extensions expressed using different suffixes
    ext_map = {
        ".jpeg": ".jpg",
        ".tif": ".tiff",
    }

    ext = Path(file_path).suffix.lower()
    if ext in ext_map:
        return ext_map[ext]
    else:
        return ext