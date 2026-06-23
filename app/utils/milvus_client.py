from app.config.settings import settings


class MilvusClient:
    _instance = None
    _collection = None
    _connected = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._conn_alias = settings.MILVUS_DEFAULT_ALIAS or "default"

    def _ensure_connected(self):
        if self._connected:
            return
        try:
            from pymilvus import connections
            import logging
            db_name = settings.MILVUS_DEFAULT_DB
            alias = settings.MILVUS_DEFAULT_ALIAS or "default"
            connections.connect(
                alias=alias,
                host=settings.MILVUS_HOST,
                port=str(settings.MILVUS_PORT),
                db_name=db_name,
            )
            logging.getLogger(__name__).info(
                "Milvus 已连接 host=%s port=%s db=%s alias=%s",
                settings.MILVUS_HOST,
                settings.MILVUS_PORT,
                db_name,
                alias,
            )
            self._connected = True
            self._conn_alias = alias
        except ImportError:
            raise ImportError("pymilvus 未安装，请执行: pip install pymilvus")
        except Exception as e:
            raise RuntimeError(f"Milvus 连接失败: {e}")

    def get_collection(self, name: str):
        self._ensure_connected()
        from pymilvus import Collection, utility

        if not utility.has_collection(name, using=self._conn_alias):
            raise ValueError(f"集合 {name} 不存在")
        return Collection(name, using=self._conn_alias)

    def _embedding_field_dim(self, collection) -> int:
        for field in collection.schema.fields:
            if field.name == "embedding":
                return field.params.get("dim")
        raise ValueError("集合缺少 embedding 字段")

    def ensure_knowledge_collection(self, dim: int | None = None):
        dim = dim or settings.EMBEDDING_DIM
        self._ensure_connected()
        from pymilvus import Collection, FieldSchema, CollectionSchema, DataType, utility

        name = settings.MILVUS_COLLECTION_KNOWLEDGE
        if utility.has_collection(name, using=self._conn_alias):
            collection = Collection(name, using=self._conn_alias)
            existing_dim = self._embedding_field_dim(collection)
            if existing_dim != dim:
                raise RuntimeError(
                    f"Milvus 集合「{name}」向量维度为 {existing_dim}，"
                    f"当前模型维度为 {dim}。请删除该集合后重新上传文档。"
                )
            return collection

        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=500),
            FieldSchema(name="doc_level", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="equipment_id", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim),
        ]
        schema = CollectionSchema(fields, description="设备知识库")
        collection = Collection(name, schema, using=self._conn_alias)

        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "COSINE",
            "params": {"nlist": 128},
        }
        collection.create_index("embedding", index_params)
        collection.load()
        return collection

    def ensure_cases_collection(self, dim: int | None = None):
        dim = dim or settings.EMBEDDING_DIM
        self._ensure_connected()
        from pymilvus import Collection, FieldSchema, CollectionSchema, DataType, utility

        name = settings.MILVUS_COLLECTION_CASES
        if utility.has_collection(name, using=self._conn_alias):
            collection = Collection(name, using=self._conn_alias)
            existing_dim = self._embedding_field_dim(collection)
            if existing_dim != dim:
                raise RuntimeError(
                    f"Milvus 集合「{name}」向量维度为 {existing_dim}，"
                    f"当前模型维度为 {dim}。请删除该集合后重新上传文档。"
                )
            return collection

        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="fault_type", dtype=DataType.VARCHAR, max_length=200),
            FieldSchema(name="resolution", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim),
        ]
        schema = CollectionSchema(fields, description="故障案例库")
        collection = Collection(name, schema, using=self._conn_alias)

        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "COSINE",
            "params": {"nlist": 128},
        }
        collection.create_index("embedding", index_params)
        collection.load()
        return collection

    def ensure_multimodal_collection(self, dim: int | None = None):
        """
        多模态知识库集合。
        存储图文混合 Chunk，包含图片路径、页码、坐标等元数据。
        """
        dim = dim or settings.EMBEDDING_DIM
        self._ensure_connected()
        from pymilvus import Collection, FieldSchema, CollectionSchema, DataType, utility

        name = settings.MILVUS_COLLECTION_MULTIMODAL
        if utility.has_collection(name, using=self._conn_alias):
            collection = Collection(name, using=self._conn_alias)
            existing_dim = self._embedding_field_dim(collection)
            if existing_dim != dim:
                raise RuntimeError(
                    f"Milvus 集合「{name}」向量维度为 {existing_dim}，"
                    f"当前模型维度为 {dim}。请删除该集合后重新上传文档。"
                )
            return collection

        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=500),
            FieldSchema(name="chunk_type", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="page_num", dtype=DataType.INT64),
            FieldSchema(name="bbox", dtype=DataType.VARCHAR, max_length=500),
            FieldSchema(name="image_path", dtype=DataType.VARCHAR, max_length=1000),
            FieldSchema(name="image_hash", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="doc_level", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="equipment_id", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim),
        ]
        schema = CollectionSchema(fields, description="多模态图文知识库")
        collection = Collection(name, schema, using=self._conn_alias)

        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "COSINE",
            "params": {"nlist": 128},
        }
        collection.create_index("embedding", index_params)
        collection.load()
        return collection


milvus_client = MilvusClient()