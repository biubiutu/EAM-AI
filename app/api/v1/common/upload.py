from fastapi import UploadFile, File, Depends

from app.core.base_router import BaseRouter
from app.core.security import get_current_user
from app.schemas.common import BaseResponse
from app.utils.minio_client import minio_client


class UploadRouter(BaseRouter):

    def _register_routes(self):
        self.router.post(
            "/file",
            response_model=BaseResponse,
            summary="上传文件(多文件)",
            description="上传任意文件到 MinIO 存储，支持多文件同时上传",
            tags=["公共-文件上传"],
        )(self.upload_files)

        return self.router

    async def upload_files(self, files: list[UploadFile] = File(...), _=Depends(get_current_user)):
        """支持单文件或多文件同时上传"""
        results = []
        for file in files:
            content = await file.read()
            result = minio_client.upload_file(content, file.filename, prefix="uploads/")
            results.append(result)
        return BaseResponse(data=results)