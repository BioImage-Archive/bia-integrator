from fastapi import HTTPException

class InvalidRequestException(HTTPException):
    def __init__(self, detail, **kwargs) -> None:
        super().__init__(422, detail, **kwargs)

class DocumentNotFound(HTTPException):
    def __init__(self, detail, **kwargs) -> None:
        super().__init__(404, detail, **kwargs)

class InvalidUpdateException(HTTPException):
    def __init__(self, detail, **kwargs) -> None:
        super().__init__(409, detail, **kwargs)
