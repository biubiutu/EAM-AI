from fastapi import UploadFile, File

from app.core.base_router import BaseRouter
from app.schemas.common import BaseResponse
import aiofiles
import os


class UploadRouter(BaseRouter):

    def __init__(self):
        super().__init__()
        self.upload_dir = "uploads"
        os.makedirs(self.upload_dir, exist_ok=True)

    def _register_routes(self):
        self.router.post(
            "/file",
            response_model=BaseResponse,
            summary="上传文件",
            description="上传任意文件到服务器，返回文件路径和文件名",
            tags=["公共-文件上传"],
        )(self.upload_file)

        return self.router

    async def upload_file(self, file: UploadFile = File(...)):
        file_path = os.path.join(self.upload_dir, file.filename)
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)
        return BaseResponse(data={"file_path": file_path, "filename": file.filename})
