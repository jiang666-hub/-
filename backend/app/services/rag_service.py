"""
RAG 检索增强生成服务 - 基于 Chroma 向量数据库
"""
import os
from typing import List, Tuple
from app.core.config import CHROMA_PERSIST_DIR, EMBEDDING_MODEL, DATA_DIR


class RAGService:
    def __init__(self):
        # 延迟导入，避免 sentence-transformers 的 Keras 兼容性问题导致整个模块加载失败
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings
            from sentence_transformers import SentenceTransformer

            self.client = chromadb.PersistentClient(
                path=CHROMA_PERSIST_DIR,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            self.embedder = SentenceTransformer(EMBEDDING_MODEL)
            self._ready = True
        except Exception as e:
            print(f"[RAG] 初始化失败，将使用关键词匹配模式: {e}")
            self._ready = False
            self.client = None
            self.embedder = None

        if self._ready:
            self._init_collections()

    def _init_collections(self):
        """初始化向量集合"""
        # 图书信息集合
        self.book_collection = self.client.get_or_create_collection(
            name="library_books",
            metadata={"description": "图书馆藏信息向量库"}
        )

        # 规章制度集合
        self.rules_collection = self.client.get_or_create_collection(
            name="library_rules",
            metadata={"description": "图书馆规章制度向量库"}
        )

        # 如果集合为空则加载数据
        if self.book_collection.count() == 0:
            self._load_books()
        if self.rules_collection.count() == 0:
            self._load_rules()

    def _load_books(self):
        """将图书信息向量化并存入 Chroma"""
        import json
        books_path = os.path.join(DATA_DIR, "books", "books.json")
        with open(books_path, "r", encoding="utf-8") as f:
            books = json.load(f)

        documents = []
        ids = []
        metadatas = []

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

        embeddings = self.embedder.encode(documents).tolist()
        self.book_collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )
        print(f"已加载 {len(books)} 本图书到向量库")

    def _load_rules(self):
        """将规章制度向量化并存入 Chroma"""
        rules_path = os.path.join(DATA_DIR, "knowledge", "rules.md")
        with open(rules_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 按 ## 二级标题分段
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
            print(f"已加载 {len(documents)} 条规章制度到向量库")

    def search_books(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """语义搜索图书"""
        if not self._ready:
            return []
        query_embedding = self.embedder.encode([query]).tolist()
        results = self.book_collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )
        return list(zip(results["ids"][0], results["distances"][0]))

    def search_rules(self, query: str, top_k: int = 3) -> List[str]:
        """语义搜索规章制度"""
        if not self._ready:
            return []
        query_embedding = self.embedder.encode([query]).tolist()
        results = self.rules_collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )
        return results["documents"][0] if results["documents"] else []


# 延迟初始化单例，避免导入时崩溃
_rag_instance = None


def get_rag_service():
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGService()
    return _rag_instance
