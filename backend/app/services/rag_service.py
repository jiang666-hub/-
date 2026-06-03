"""
RAG 检索增强生成服务 - 基于 Chroma 向量数据库
Render 免费版内存有限，RAG 可能不可用，此时自动降级为关键词搜索
"""
import os
from typing import List, Tuple
from app.core.config import CHROMA_PERSIST_DIR, EMBEDDING_MODEL, DATA_DIR


class RAGService:
    def __init__(self):
        self._ready = False
        self.client = None
        self.embedder = None

        # 检查 chromadb 和 sentence_transformers 是否可用
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings
        except ImportError:
            print("[RAG] chromadb 未安装，RAG 服务不可用")
            return

        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            print("[RAG] sentence-transformers 未安装，RAG 服务不可用")
            return

        try:
            self.client = chromadb.PersistentClient(
                path=CHROMA_PERSIST_DIR,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            self.embedder = SentenceTransformer(EMBEDDING_MODEL)
            self._ready = True
        except Exception as e:
            print(f"[RAG] 初始化失败: {e}")
            return

        if self._ready:
            self._init_collections()

    def _init_collections(self):
        """初始化向量集合"""
        self.book_collection = self.client.get_or_create_collection(
            name="library_books",
            metadata={"description": "图书馆藏信息向量库"}
        )
        self.rules_collection = self.client.get_or_create_collection(
            name="library_rules",
            metadata={"description": "图书馆规章制度向量库"}
        )

        if self.book_collection.count() == 0:
            self._load_books()
        if self.rules_collection.count() == 0:
            self._load_rules()

    def _load_books(self):
        import json
        books_path = os.path.join(DATA_DIR, "books", "books.json")
        with open(books_path, "r", encoding="utf-8") as f:
            books = json.load(f)

        documents = []
        ids = []
        metadatas = []
        batch_size = 200

        for book in books:
            text = (
                f"《{book['title']}》，作者：{book['author']}，"
                f"出版社：{book['publisher']}，类别：{book['category']}，"
                f"简介：{book['description']}，标签：{'、'.join(book['tags'])}，"
                f"位置：{book['location']}，索书号：{book['shelf_number']}，"
                f"馆藏：{book['stock']}本，可借：{book['available']}本"
            )
            documents.append(text)
            ids.append(str(book["id"]))
            metadatas.append({
                "title": book["title"],
                "author": book["author"],
                "category": book["category"]
            })

        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            batch_meta = metadatas[i:i+batch_size]
            embeddings = self.embedder.encode(batch_docs).tolist()
            self.book_collection.add(
                ids=batch_ids,
                documents=batch_docs,
                embeddings=embeddings,
                metadatas=batch_meta
            )
        print(f"[RAG] 已加载 {len(books)} 本图书到向量库")

    def _load_rules(self):
        rules_path = os.path.join(DATA_DIR, "knowledge", "rules.md")
        with open(rules_path, "r", encoding="utf-8") as f:
            content = f.read()

        sections = content.split("\n## ")
        documents = []
        ids = []

        for i, section in enumerate(sections):
            if section.strip():
                documents.append(section.strip())
                ids.append(f"rule_{i}")

        if documents:
            embeddings = self.embedder.encode(documents).tolist()
            self.rules_collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings
            )
            print(f"[RAG] 已加载 {len(documents)} 条规章制度到向量库")

    def search_books(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        if not self._ready:
            return []
        query_embedding = self.embedder.encode([query]).tolist()
        results = self.book_collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )
        return list(zip(results["ids"][0], results["distances"][0]))

    def search_rules(self, query: str, top_k: int = 3) -> List[str]:
        if not self._ready:
            return []
        query_embedding = self.embedder.encode([query]).tolist()
        results = self.rules_collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )
        return results["documents"][0] if results["documents"] else []


# 延迟初始化单例
_rag_instance = None


def get_rag_service():
    global _rag_instance
    if _rag_instance is None:
        try:
            _rag_instance = RAGService()
        except Exception:
            _rag_instance = False
    return _rag_instance if _rag_instance is not False else None
