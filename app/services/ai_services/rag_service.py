from app.utils.ai_client import ai_client
from app.utils.milvus_client import milvus_client
import os


class RAGService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._embedding_model = None
        self._text_splitter = None

    def _load_embedding(self):
        if self._embedding_model is None:
            from sentence_transformers import SentenceTransformer
            self._embedding_model = SentenceTransformer("shibing624/text2vec-base-chinese")

    def _load_splitter(self):
        if self._text_splitter is None:
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            self._text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    def _ensure_collections(self):
        self.knowledge_collection = milvus_client.ensure_knowledge_collection(dim=768)
        self.cases_collection = milvus_client.ensure_cases_collection(dim=768)

    async def ingest_manual(self, file_path: str, source: str = "") -> list:
        self._load_splitter()
        self._load_embedding()
        self._ensure_collections()

        text = self._extract_text(file_path)
        chunks = self._text_splitter.split_text(text)

        count = 0
        for chunk in chunks:
            embedding = self._embedding_model.encode(chunk).tolist()
            self.knowledge_collection.insert([{
                "content": chunk,
                "source": source or os.path.basename(file_path),
                "embedding": embedding,
            }])
            count += 1
        self.knowledge_collection.flush()
        return list(range(count))

    async def query_knowledge(self, question: str, top_k: int = 3) -> dict:
        self._load_embedding()
        self._ensure_collections()

        query_embedding = self._embedding_model.encode(question).tolist()
        self.knowledge_collection.load()

        search_params = {"metric_type": "L2", "params": {"nprobe": 16}}
        results = self.knowledge_collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            output_fields=["content", "source"],
        )

        docs = []
        for hits in results:
            for hit in hits:
                docs.append({
                    "content": hit.entity.get("content"),
                    "source": hit.entity.get("source"),
                    "distance": hit.distance,
                })

        context = "\n\n".join([d["content"] for d in docs])
        prompt = f"""你是设备维修专家助手。请根据以下设备资料回答问题。

【设备资料】
{context}

【用户问题】
{question}

请给出详细排查步骤，并注明信息来源。"""

        answer = await ai_client.chat(prompt)

        return {
            "answer": answer,
            "sources": [{"source": d["source"], "distance": d["distance"]} for d in docs],
        }

    async def search_fault_cases(self, query: str, top_k: int = 5) -> dict:
        self._load_embedding()
        self._ensure_collections()

        query_embedding = self._embedding_model.encode(query).tolist()
        self.cases_collection.load()

        search_params = {"metric_type": "L2", "params": {"nprobe": 16}}
        results = self.cases_collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            output_fields=["content", "fault_type", "resolution"],
        )

        cases = []
        for hits in results:
            for hit in hits:
                cases.append({
                    "content": hit.entity.get("content"),
                    "fault_type": hit.entity.get("fault_type"),
                    "resolution": hit.entity.get("resolution"),
                    "distance": hit.distance,
                })

        return {"cases": cases}

    async def ingest_fault_case(self, fault_desc: str, fault_type: str, resolution: str):
        self._load_embedding()
        self._ensure_collections()

        embedding = self._embedding_model.encode(fault_desc).tolist()
        self.cases_collection.insert([{
            "content": fault_desc,
            "fault_type": fault_type,
            "resolution": resolution,
            "embedding": embedding,
        }])
        self.cases_collection.flush()

    def _extract_text(self, file_path: str) -> str:
        if file_path.endswith(".pdf"):
            try:
                import pdfplumber
                text = ""
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                return text
            except ImportError:
                raise ImportError("pdfplumber 未安装，请执行: pip install pdfplumber")
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()


rag_service = RAGService()