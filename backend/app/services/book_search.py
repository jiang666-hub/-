"""
图书检索服务 - 关键词搜索 + 语义搜索
"""
import json
import os
from typing import List
import jieba
from app.core.config import DATA_DIR
from app.models.schemas import Book


class BookSearchService:
    def __init__(self):
        self.books: List[Book] = []
        self._load_books()

    def _load_books(self):
        """加载图书数据"""
        books_path = os.path.join(DATA_DIR, "books", "books.json")
        with open(books_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.books = [Book(**item) for item in data]

    def keyword_search(self, query: str, top_k: int = 5) -> List[Book]:
        """
        关键词搜索：对书名、作者、标签、分类进行多字段匹配
        """
        query_lower = query.lower()
        query_words = set(jieba.cut(query))

        scored_books = []
        for book in self.books:
            score = 0
            text_to_search = (
                book.title + " " + book.author + " " +
                book.category + " " + " ".join(book.tags) +
                " " + book.description
            ).lower()

            # 精确匹配加分
            if query_lower in book.title.lower():
                score += 10
            if query_lower in book.author.lower():
                score += 8
            if query_lower in book.category.lower():
                score += 5

            # 分词匹配加分
            for word in query_words:
                if word in text_to_search:
                    score += 2

            # 标签匹配加分
            for tag in book.tags:
                for word in query_words:
                    if word in tag.lower():
                        score += 3

            if score > 0:
                scored_books.append((book, score))

        scored_books.sort(key=lambda x: x[1], reverse=True)
        return [book for book, _ in scored_books[:top_k]]

    def get_by_id(self, book_id: int) -> Book:
        for book in self.books:
            if book.id == book_id:
                return book
        return None

    def get_all_books(self) -> List[Book]:
        return self.books


# 单例
book_search_service = BookSearchService()
