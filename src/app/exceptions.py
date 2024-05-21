from fastapi import HTTPException, status


class UnAuthorizedError(HTTPException):
    def __init__(self) -> None:
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = "Could not validate user, please, login again"