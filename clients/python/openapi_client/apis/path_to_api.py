import typing_extensions

from openapi_client.paths import PathValues
from openapi_client.apis.paths.studies_ import Studies
from openapi_client.apis.paths.studies_study_id_refresh_counts import StudiesStudyIdRefreshCounts
from openapi_client.apis.paths.studies_study_id import StudiesStudyId
from openapi_client.apis.paths.studies_study_id_file_references import StudiesStudyIdFileReferences
from openapi_client.apis.paths.studies_search_images_by_alias import StudiesSearchImagesByAlias
from openapi_client.apis.paths.studies_images import StudiesImages
from openapi_client.apis.paths.studies_study_id_images import StudiesStudyIdImages
from openapi_client.apis.paths.studies_study_id_images_image_id_ome_metadata import StudiesStudyIdImagesImageIdOmeMetadata
from openapi_client.apis.paths.admin_health_check import AdminHealthCheck
from openapi_client.apis.paths.admin_pipelines import AdminPipelines

PathToApi = typing_extensions.TypedDict(
    'PathToApi',
    {
        PathValues.STUDIES_: Studies,
        PathValues.STUDIES_STUDY_ID_REFRESH_COUNTS: StudiesStudyIdRefreshCounts,
        PathValues.STUDIES_STUDY_ID: StudiesStudyId,
        PathValues.STUDIES_STUDY_ID_FILE_REFERENCES: StudiesStudyIdFileReferences,
        PathValues.STUDIES_SEARCH_IMAGES_BYALIAS: StudiesSearchImagesByAlias,
        PathValues.STUDIES_IMAGES: StudiesImages,
        PathValues.STUDIES_STUDY_ID_IMAGES: StudiesStudyIdImages,
        PathValues.STUDIES_STUDY_ID_IMAGES_IMAGE_ID_OME_METADATA: StudiesStudyIdImagesImageIdOmeMetadata,
        PathValues.ADMIN_HEALTHCHECK: AdminHealthCheck,
        PathValues.ADMIN_PIPELINES: AdminPipelines,
    }
)

path_to_api = PathToApi(
    {
        PathValues.STUDIES_: Studies,
        PathValues.STUDIES_STUDY_ID_REFRESH_COUNTS: StudiesStudyIdRefreshCounts,
        PathValues.STUDIES_STUDY_ID: StudiesStudyId,
        PathValues.STUDIES_STUDY_ID_FILE_REFERENCES: StudiesStudyIdFileReferences,
        PathValues.STUDIES_SEARCH_IMAGES_BYALIAS: StudiesSearchImagesByAlias,
        PathValues.STUDIES_IMAGES: StudiesImages,
        PathValues.STUDIES_STUDY_ID_IMAGES: StudiesStudyIdImages,
        PathValues.STUDIES_STUDY_ID_IMAGES_IMAGE_ID_OME_METADATA: StudiesStudyIdImagesImageIdOmeMetadata,
        PathValues.ADMIN_HEALTHCHECK: AdminHealthCheck,
        PathValues.ADMIN_PIPELINES: AdminPipelines,
    }
)
