from fastapi import HTTPException, status


class BaseProjectException(HTTPException):
    default_message = None
    status_code = None

    def __init__(self, detail: str | None = None):
        super().__init__(
            status_code=self.status_code,
            detail=detail if detail else self.default_message,
        )


class NotFoundException(BaseProjectException):
    default_message = "Not Found"
    status_code = status.HTTP_404_NOT_FOUND


class AlreadyExistsException(BaseProjectException):
    default_message = "Object already exists"
    status_code = status.HTTP_400_BAD_REQUEST


class SelfLikeException(BaseProjectException):
    default_message = "Selfliking doesn't allowed"
    status_code = status.HTTP_400_BAD_REQUEST


class SelfMatchException(BaseProjectException):
    default_message = "Selfmatching doesn't allowed"
    status_code = status.HTTP_400_BAD_REQUEST


class PermissionDeniedException(BaseProjectException):
    default_message = "You don't have acces to object"
    status_code = status.HTTP_403_FORBIDDEN
