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

    def _ensure_connected(self):
        if self._connected:
            return
        try:
            from pymilvus import connections
            connections.connect(
                alias="default",
                host=settings.MILVUS_HOST,
                port=settings.MILVUS_PORT,
            )
            self._connected = True
        except ImportError:
            raise ImportError("pymilvus 未安装，请执行: pip install pymilvus")
        except Exception as e:
            raise RuntimeError(f"Milvus 连接失败: {e}")

    def get_collection(self, name: str):
        self._ensure_connected()
        from pymilvus import Collection, utility

        if not utility.has_collection(name):
            raise ValueError(f"集合 {name} 不存在")
        return Collection(name)

    def ensure_knowledge_collection(self, dim: int = 768):
        self._ensure_connected()
        from pymilvus import Collection, FieldSchema, CollectionSchema, DataType, utility

        name = settings.MILVUS_COLLECTION_KNOWLEDGE
        if utility.has_collection(name):
            return Collection(name)

        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=500),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim),
        ]
        schema = CollectionSchema(fields, description="设备知识库")
        collection = Collection(name, schema)

        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 128},
        }
        collection.create_index("embedding", index_params)
        collection.load()
        return collection

    def ensure_cases_collection(self, dim: int = 768):
        self._ensure_connected()
        from pymilvus import Collection, FieldSchema, CollectionSchema, DataType, utility

        name = settings.MILVUS_COLLECTION_CASES
        if utility.has_collection(name):
            return Collection(name)

        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="fault_type", dtype=DataType.VARCHAR, max_length=200),
            FieldSchema(name="resolution", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim),
        ]
        schema = CollectionSchema(fields, description="故障案例库")
        collection = Collection(name, schema)

        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 128},
        }
        collection.create_index("embedding", index_params)
        collection.load()
        return collection


milvus_client = MilvusClient()