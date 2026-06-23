"""
Vanna Text2SQL 训练数据流水线
"""
import json
import os
import logging
import requests
from app.config.settings import settings
from app.utils.minio_client import minio_client

logger = logging.getLogger(__name__)


class VannaTrainingService:
    _instance = None
    _session = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._local_dir = os.path.join(settings.BASE_DIR, "data", "vanna") if hasattr(settings, "BASE_DIR") else "data/vanna"
        os.makedirs(self._local_dir, exist_ok=True)
        self._minio_training_bucket = "vanna-training-data"

    def _get_session(self):
        if self._session is None:
            import sqlalchemy as sa
            if settings.MYSQL_URL:
                self._session = sa.create_engine(settings.MYSQL_URL)
        return self._session

    def generate_ddl(self) -> str:
        """从数据库抽取 DDL"""
        engine = self._get_session()
        if not engine:
            return ""
        from sqlalchemy import inspect
        inspector = inspect(engine)
        ddl_parts = []
        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            cols = []
            for col in columns:
                col_type = str(col["type"])
                nullable = "NULL" if col.get("nullable", True) else "NOT NULL"
                default = f"DEFAULT {col['default']}" if col.get("default") is not None else ""
                comment = f"COMMENT '{col.get('comment', '')}'" if col.get("comment") else ""
                cols.append(f"  `{col['name']}` {col_type} {nullable} {default} {comment}")
            ddl_parts.append(f"CREATE TABLE `{table_name}` (\n" + ",\n".join(cols) + "\n);")
        return "\n\n".join(ddl_parts)

    def generate_training_data(self) -> list[dict]:
        """查询操作记录生成 training data (question -> sql)"""
        # 从审计日志、工单数据等提取自然语言→SQL对
        return []  # Phase 5 full: 需从操作日志中提取

    def train_vanna_remote(self) -> bool:
        """推送训练数据到 Vanna 远程服务"""
        ddl = self.generate_ddl()
        training_data = self.generate_training_data()

        payload = {"ddl": ddl, "training_data": training_data}
        try:
            resp = requests.post(
                f"{settings.AI_BASE_URL.rstrip('/')}/v1/vanna/train",
                headers={"Authorization": f"Bearer {settings.AI_API_KEY}"},
                json=payload,
                timeout=60,
            )
            if resp.status_code < 400:
                logger.info("Vanna 训练数据推送成功")
                return True
            logger.warning("Vanna 训练推送失败: %s", resp.text[:200])
            return False
        except Exception as e:
            logger.warning("Vanna 远程训练失败: %s", e)
            return False

    def sync_ddl_to_minio(self):
        """同步 DDL 到 MinIO"""
        ddl = self.generate_ddl()
        bucket = self._minio_training_bucket
        try:
            minio_client.upload_file(
                ddl.encode("utf-8"),
                "schema.sql",
                bucket=bucket,
                prefix="training/",
            )
            logger.info("DDL 已同步到 MinIO: %s/training/schema.sql", bucket)
        except Exception as e:
            logger.debug("DDL 同步到 MinIO 失败: %s", e)


vanna_training_service = VannaTrainingService()