"""
后端启动入口 - 轻量版（无需 ChromaDB 向量库）
先确保基础功能可用，等 sentence-transformers 安装完后会自动启用 RAG
"""
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 先把后端目录加入 path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import DATA_DIR, CHROMA_PERSIST_DIR
from app.main import app
import uvicorn

print("=" * 50)
print("  图书馆图文智能体 - 后端服务")
print("=" * 50)

# 检查依赖
missing = []
try:
    import chromadb
    print(f"[OK] chromadb 已安装")
except ImportError:
    missing.append("chromadb")

try:
    from sentence_transformers import SentenceTransformer
    print(f"[OK] sentence-transformers 已安装")
except ImportError:
    missing.append("sentence-transformers")

try:
    import jieba
    print(f"[OK] jieba 已安装")
except ImportError:
    missing.append("jieba")

if missing:
    print(f"\n[WARN] 以下包未安装: {', '.join(missing)}")
    print("[INFO] 关键词搜索模式可用，RAG 语义搜索暂时不可用")
    print("[INFO] 安装命令: pip install chromadb sentence-transformers")
else:
    print("\n[OK] 所有依赖已就绪，RAG 语义搜索已启用")

print(f"\n[INFO] 数据目录: {DATA_DIR}")
print(f"[INFO] 向量库路径: {CHROMA_PERSIST_DIR}")
print(f"\n服务启动: http://localhost:8000")
print(f"API 文档: http://localhost:8000/docs")
print("=" * 50)

uvicorn.run(app, host="0.0.0.0", port=8000)
