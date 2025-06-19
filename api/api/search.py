from fastapi import APIRouter, Depends, Query
from api import constants
from api.public import models_public
from pydantic.alias_generators import to_snake
from typing import List, Annotated, Optional, Type
from api.models.repository import Repository
from api.app import get_db
from api.models.api import Pagination
import bia_shared_datamodels.bia_data_model as shared_data_models
import re

router = APIRouter(
    prefix="/search", tags=[constants.OPENAPI_TAG_PUBLIC, constants.OPENAPI_TAG_PRIVATE]
)


@router.get("/study/accession")
async def searchStudyByAccession(
    accession_id: str, db: Annotated[Repository, Depends(get_db)]
) -> Optional[shared_data_models.Study]:
    studies = await db.get_docs(
        {"accession_id": accession_id},
        shared_data_models.Study,
        pagination=Pagination(start_from_uuid=None, page_size=1),
    )

    if not studies:
        return None
    else:
        return studies[0]


@router.get("/image_representation/file_uri_fragment")
async def searchImageRepresentationByFileUri(
    file_uri: Annotated[str, Query(min_length=5, max_length=1000)],
    db: Annotated[Repository, Depends(get_db)],
    pagination: Annotated[Pagination, Depends()],
) -> List[shared_data_models.ImageRepresentation]:
    return await db.get_docs(
        {"file_uri": {"$regex": f"^.*{re.escape(file_uri)}.*$"}},
        shared_data_models.ImageRepresentation,
        pagination=pagination,
    )


@router.get("/file_reference/by_path_name")
async def searchFileReferenceByPathName(
    path_name: Annotated[str, Query(min_length=5, max_length=1000)],
    db: Annotated[Repository, Depends(get_db)],
    pagination: Annotated[Pagination, Depends()],
    study_uuid: shared_data_models.UUID,
) -> List[shared_data_models.FileReference]:
    study = await db.get_doc(study_uuid, shared_data_models.Study)
    pipeline = [
        {
            "$match": {
                "submitted_in_study_uuid": study_uuid,
            }
        },
        {
            "$lookup": {
                "from": "bia_integrator",
                "let": {"dataset_uuid": "$uuid"},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {
                                        "$eq": [
                                            "$submission_dataset_uuid",
                                            "$$dataset_uuid",
                                        ]
                                    },
                                    {"$eq": ["$file_path", path_name]},
                                ]
                            }
                        }
                    },
                    {"$project": {"_id": 0}},
                ],
                "as": "files",
            }
        },
        {
            "$project": {
                "_id": 0,
                "uuid": 1,
                "submitted_in_study_uuid": 1,
                "files": 1,
            }
        },
    ]
    results = await db.aggregate(pipeline)
    if results:
        results = [x for res in results for x in res["files"]][: pagination.page_size]
    return results


def make_search_items(t: Type[shared_data_models.DocumentMixin]):
    async def get_items(
        db: Annotated[Repository, Depends(get_db)],
        pagination: Annotated[Pagination, Depends()],
        filter_uuid: Annotated[List[shared_data_models.UUID], Query()] = None,
    ) -> List[t]:
        """
        Get all objects with a certain type
        """

        doc_filter = {}
        if filter_uuid:
            doc_filter["uuid"] = {"$in": filter_uuid}

        return await db.get_docs(
            doc_filter,
            t,
            pagination=pagination,
        )

    return get_items


def make_router() -> APIRouter:
    for t in models_public:
        router.add_api_route(
            f"/{to_snake(t.__name__)}",
            response_model=List[t],
            operation_id=f"search{t.__name__}",
            summary=f"Search all objects of type {t.__name__}",
            methods=["GET"],
            endpoint=make_search_items(t),
        )

    return router
