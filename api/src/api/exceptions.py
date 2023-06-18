from fastapi import HTTPException

# @TODO: Use status constants to give more informative results for batch operations

STATUS_INVALID_REQUEST=422
class InvalidRequestException(HTTPException):
    def __init__(self, detail, **kwargs) -> None:
        super().__init__(STATUS_INVALID_REQUEST, detail, **kwargs)

STATUS_DOCUMENT_NOT_FOUND=404
class DocumentNotFound(HTTPException):
    def __init__(self, detail, **kwargs) -> None:
        super().__init__(STATUS_DOCUMENT_NOT_FOUND, detail, **kwargs)

STATUS_INVALID_UPDATE=409
class InvalidUpdateException(HTTPException):
    def __init__(self, detail, **kwargs) -> None:
        super().__init__(STATUS_INVALID_UPDATE, detail, **kwargs)
