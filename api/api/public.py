from fastapi import APIRouter

# ?
import bia_shared_datamodels.bia_data_model as shared_data_models

router = APIRouter()
models_public = [
    shared_data_models.Study,
    shared_data_models.ImageAnnotationDataset,
    shared_data_models.ExperimentalImagingDataset,
    shared_data_models.AnnotationFileReference,
    shared_data_models.FileReference,
]

for t in models_public:

    @router.get("/" + t.__name__, response_model=t)
    def get_item(uuid: shared_data_models.UUID):
        pass
