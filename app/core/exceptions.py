from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(self, code: int = 400, msg: str = "请求错误", http_status: int = 400):
        self.code = code
        self.msg = msg
        super().__init__(status_code=http_status, detail={"code": code, "msg": msg})


class NotFoundException(AppException):
    def __init__(self, msg: str = "资源不存在"):
        super().__init__(code=404, msg=msg, http_status=status.HTTP_404_NOT_FOUND)


class UnauthorizedException(AppException):
    def __init__(self, msg: str = "未授权访问"):
        super().__init__(code=401, msg=msg, http_status=status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(AppException):
    def __init__(self, msg: str = "权限不足"):
        super().__init__(code=403, msg=msg, http_status=status.HTTP_403_FORBIDDEN)


class BadRequestException(AppException):
    def __init__(self, msg: str = "请求参数错误"):
        super().__init__(code=400, msg=msg, http_status=status.HTTP_400_BAD_REQUEST)


class InternalException(AppException):
    def __init__(self, msg: str = "服务器内部错误"):
        super().__init__(code=500, msg=msg, http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)