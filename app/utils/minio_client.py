"""MinIO 文件存储客户端"""
import os
import io
import uuid
from datetime import timedelta
from typing import Optional

from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class MinioClient:
    """统一 MinIO 文件存储客户端"""

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is not None:
            return self._client
        from minio import Minio
        self._client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self._ensure_bucket(settings.MINIO_BUCKET)
        self._ensure_bucket(settings.KB_BUCKET_NAME)
        return self._client

    def _ensure_bucket(self, bucket: str):
        client = self._client
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
            logger.info(f"MinIO 桶 {bucket} 已创建")

    def put_object_exact(
        self,
        file_data: bytes,
        object_name: str,
        bucket: Optional[str] = None,
        content_type: Optional[str] = None,
    ) -> dict:
        """按指定对象名上传（用于与数据库文件路径精准匹配）"""
        client = self._get_client()
        bucket = bucket or settings.KB_BUCKET_NAME
        ext = os.path.splitext(object_name)[1]
        file_size = len(file_data)
        client.put_object(
            bucket,
            object_name,
            io.BytesIO(file_data),
            file_size,
            content_type=content_type or self._guess_content_type(ext),
        )
        logger.info(f"文件已上传到 MinIO: {bucket}/{object_name} ({file_size} bytes)")
        return {
            "bucket": bucket,
            "object_name": object_name,
            "filename": os.path.basename(object_name),
            "size": file_size,
        }

    def upload_file(
        self,
        file_data: bytes,
        filename: str,
        bucket: Optional[str] = None,
        prefix: str = "",
    ) -> dict:
        """
        上传文件到 MinIO

        参数:
            file_data: 文件二进制内容
            filename: 原始文件名
            bucket: 桶名，默认 settings.MINIO_BUCKET
            prefix: 路径前缀（如 "uploads/manuals/"）

        返回:
            {"bucket": str, "object_name": str, "url": str, "filename": str}
        """
        client = self._get_client()
        bucket = bucket or settings.MINIO_BUCKET

        ext = os.path.splitext(filename)[1]
        object_name = f"{prefix}{uuid.uuid4().hex}{ext}"

        file_size = len(file_data)
        client.put_object(
            bucket,
            object_name,
            io.BytesIO(file_data),
            file_size,
            content_type=self._guess_content_type(ext),
        )

        logger.info(f"文件已上传到 MinIO: {bucket}/{object_name} ({file_size} bytes)")
        return {
            "bucket": bucket,
            "object_name": object_name,
            "filename": filename,
            "size": file_size,
        }

    def get_file_url(self, bucket: str, object_name: str, expires: int = 3600) -> str:
        """获取文件的预签名 URL"""
        client = self._get_client()
        url = client.presigned_get_object(bucket, object_name, expires=timedelta(seconds=expires))
        return url

    def download_file(self, bucket: str, object_name: str) -> bytes:
        """下载文件内容"""
        client = self._get_client()
        response = client.get_object(bucket, object_name)
        data = response.read()
        response.close()
        response.release_conn()
        return data

    def list_files(self, bucket: str, prefix: str = "", recursive: bool = True) -> list[dict]:
        """列出 MinIO 桶中的文件列表"""
        client = self._get_client()
        objects = client.list_objects(bucket, prefix=prefix, recursive=recursive)
        return [
            {
                "object_name": obj.object_name,
                "filename": os.path.basename(obj.object_name),
                "size": obj.size,
                "last_modified": obj.last_modified.isoformat() if obj.last_modified else "",
            }
            for obj in objects
        ]

    @staticmethod
    def _guess_content_type(ext: str) -> str:
        mapping = {
            ".pdf": "application/pdf",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".xls": "application/vnd.ms-excel",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".txt": "text/plain",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".json": "application/json",
        }
        return mapping.get(ext.lower(), "application/octet-stream")


minio_client = MinioClient()