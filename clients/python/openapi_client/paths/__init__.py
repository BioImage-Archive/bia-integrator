# do not import all endpoints into this module because that uses a lot of memory and stack frames
# if you need the ability to import all endpoints from this module, import them with
# from openapi_client.apis.path_to_api import path_to_api

import enum


class PathValues(str, enum.Enum):
    STUDIES_ = "/studies/"
    STUDIES_STUDY_ID_REFRESH_COUNTS = "/studies/{study_id}/refresh_counts"
    STUDIES_STUDY_ID = "/studies/{study_id}"
    STUDIES_STUDY_ID_FILE_REFERENCES = "/studies/{study_id}/file_references"
    STUDIES_SEARCH_IMAGES_BYALIAS = "/studies/search/images/by-alias"
    STUDIES_IMAGES = "/studies/images"
    STUDIES_STUDY_ID_IMAGES = "/studies/{study_id}/images"
    STUDIES_STUDY_ID_IMAGES_IMAGE_ID_OME_METADATA = "/studies/{study_id}/images/{image_id}/ome_metadata"
    ADMIN_HEALTHCHECK = "/admin/health-check"
    ADMIN_PIPELINES = "/admin/pipelines"
