"""
API 路由
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse, SearchRequest
from app.services.intent_router import intent_router
from app.services.book_search import book_search_service

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    主对话接口：接收用户消息，路由到对应处理模块
    支持 category 参数，按分类筛选推荐结果
    """
    try:
        result = intent_router.route(request.message, request.history, request.category)
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_books(request: SearchRequest):
    """
    图书搜索接口
    """
    books = book_search_service.keyword_search(request.query, request.top_k)
    return {
        "query": request.query,
        "total": len(books),
        "books": [b.model_dump() for b in books]
    }


@router.get("/books")
async def list_books(category: str = None, page: int = 1, size: int = 20):
    """
    图书列表接口，支持按分类筛选
    """
    books = book_search_service.get_all_books()
    if category:
        books = [b for b in books if b.category == category]

    total = len(books)
    start = (page - 1) * size
    end = start + size

    return {
        "total": total,
        "page": page,
        "size": size,
        "books": [b.model_dump() for b in books[start:end]]
    }


@router.get("/books/{book_id}")
async def get_book(book_id: int):
    """
    图书详情接口
    """
    book = book_search_service.get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="图书不存在")
    return book.model_dump()


@router.get("/categories")
async def list_categories():
    """
    获取所有分类
    """
    books = book_search_service.get_all_books()
    categories = list(set(b.category for b in books))
    return {"categories": categories}
