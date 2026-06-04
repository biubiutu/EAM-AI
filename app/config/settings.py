import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "AI-EAM"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    LLM_MODEL: str = "qwen3.5:2b"
    EMBEDDING_MODEL: str = "nomic-embed-text:latest"
    LLM_STRATEGY: str = "ollama"
    EMBEDDING_STRATEGY: str = "ollama"
    LLM_ENV: str = "ollama"

    SILICON_FLOW_API_KEY: str = "sk-cmboxviixeoqsjpfqqpcwuiwdmyjcgvcdfbjmofwknutltap"
    SILICON_FLOW_BASE_URL: str = "https://api.siliconflow.cn/v1"
    SILICON_FLOW_LLM_URL: str = "https://api.siliconflow.cn/v1/chat/completions"
    SILICON_FLOW_EMBEDDING_URL: str = "https://api.siliconflow.cn/v1/embeddings"
    SILICON_FLOW_LLM_MODEL: str = "deepseek-ai/DeepSeek-R1"
    SILICON_FLOW_EMBEDDING_MODEL: str = "BAAI/bge-large-zh-v1.5"

    API_KEY: Optional[str] = "sk-04e55439d22d49d3bb003b164fba4771"
    AI_API_KEY: Optional[str] = "sk-04e55439d22d49d3bb003b164fba4771"
    AI_BASE_URL: str = "https://api.deepseek.com/v1"
    AI_MODEL: str = "deepseek-v4-flash"
    DEEPSEEK_API_KEY: Optional[str] = "sk-04e55439d22d49d3bb003b164fba4771"
    BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-v4-flash"
    DEEPSEEK_LLM_URL: str = "https://api.deepseek.com/v1/chat/completions"
    DEEPSEEK_EMBEDDING_URL: str = "https://api.deepseek.com/v1/embeddings"

    DIFY_API_KEY: Optional[str] = None
    WORKFLOW_ID: Optional[str] = None
    DIFY_BASE_URL: str = "http://127.0.0.1"
    DIFY_TIME_OUT: int = 600

    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 5379
    REDIS_DB: int = 0
    REDIS_URL: str = "redis://127.0.0.1:6379/0"
    REDIS_MAX_CONNECTIONS: int = 1000
    REDIS_SOCKET_TIMEOUT: int = 30
    REDIS_SOCKET_CONNECT_TIMEOUT: int = 5

    MINIO_ENDPOINT: str = "127.0.0.1:9100"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "vanna-training-data"
    MINIO_SECURE: bool = False
    KB_BUCKET_NAME: str = "knowledge-base"

    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "123456"
    MYSQL_HOST: str = "127.0.0.1"
    MYSQL_PORT: int = 3306
    MYSQL_DB: str = "eam_ai"
    MYSQL_URI: str = "mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@${MYSQL_HOST}:${MYSQL_PORT}/${MYSQL_DB}"

    MILVUS_URI: str = "http://127.0.0.1:19530"
    MILVUS_HOST: str = "127.0.0.1"
    MILVUS_PORT: int = 19530
    MILVUS_DEFAULT_COLLECTION: str = "nrs2002_collection_v2"
    MILVUS_DEFAULT_ALIAS: str = "default"
    MILVUS_DEFAULT_DB: str = "default"
    MILVUS_COLLECTION_KNOWLEDGE: str = "equipment_knowledge"
    MILVUS_COLLECTION_CASES: str = "fault_cases"

    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = "San20260"

    JIEBA_USER_DICT: str = "./jieba_user_dict.txt"
    JIEBA_STOPWORDS_PATH: str = "jieba_stopwords.txt"

    WHISPER_MODEL_SIZE: str = "base"

    JWT_SECRET_KEY: str = "eam-ai-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    ENV: str = "production"

    def get_database_url(self) -> str:
        return f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
