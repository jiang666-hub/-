"""
图书馆智能体 - 核心配置
"""
import os

# 项目路径
# config.py -> app/core/ -> 上两级是 backend 根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Chroma 向量数据库路径
CHROMA_PERSIST_DIR = os.path.join(BASE_DIR, "chroma_db")

# LLM 配置 - 使用 DeepSeek API（通过代理）
LLM_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "your-deepseek-api-key")
LLM_API_BASE = os.environ.get("DEEPSEEK_API_BASE", "https://api.deepseek.com")
LLM_MODEL = "deepseek-chat"

# 嵌入模型（本地运行，不需要 API Key）
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

# CORS 配置
CORS_ORIGINS = ["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"]
