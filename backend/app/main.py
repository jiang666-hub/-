"""
图书馆智能体 - FastAPI 主入口
同时托管前端静态文件 + API 服务，一个端口全搞定
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routes import router
from app.core.config import CORS_ORIGINS

app = FastAPI(
    title="图书馆图文智能体",
    description="支持图书检索、推荐、规章制度问答的智能助手",
    version="1.0.0"
)

# CORS 配置（部署后允许任意来源）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

# 前端静态文件路径
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")

if os.path.exists(STATIC_DIR):
    # 挂载静态资源（JS/CSS/图片等）
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str = ""):
        """兜底路由：所有非 API 请求返回前端 index.html（SPA 路由支持）"""
        file_path = os.path.join(STATIC_DIR, full_path) if full_path else os.path.join(STATIC_DIR, "index.html")
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))

    @app.get("/")
    async def root():
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))
else:
    @app.get("/")
    async def root():
        return {
            "message": "图书馆图文智能体 API",
            "docs": "/docs",
            "version": "1.0.0"
        }
