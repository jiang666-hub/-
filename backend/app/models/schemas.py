"""
数据模型定义
"""
from pydantic import BaseModel
from typing import Optional, List


class Book(BaseModel):
    id: int
    isbn: str
    title: str
    author: str
    publisher: str
    publish_year: int
    category: str
    location: str
    shelf_number: str
    stock: int
    available: int
    cover_url: str
    description: str
    tags: List[str]


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = []
    category: Optional[str] = None  # 指定分类推荐


class ChatResponse(BaseModel):
    answer: str
    books: Optional[List[Book]] = None
    source: str = "knowledge"


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
