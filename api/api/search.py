from fastapi import APIRouter, Depends, Query
from api import constants
from typing import List, Annotated, Optional
from api.models.repository import Repository, get_db
from api.models.api import Pagination
import bia_shared_datamodels.bia_data_model as shared_data_models
import re

router = APIRouter(prefix="/search", tags=[constants.OPENAPI_TAG_PUBLIC])


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


def make_router() -> APIRouter:
    return router
