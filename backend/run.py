"""
启动脚本：初始化向量库并启动服务
"""
import subprocess
import sys
import os

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # 安装依赖
    print("正在安装依赖...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"])

    print("正在初始化向量数据库...")
    from app.services.rag_service import rag_service
    # 触发初始化，加载数据到向量库
    print(f"图书向量数: {rag_service.book_collection.count()}")
    print(f"规章向量数: {rag_service.rules_collection.count()}")

    print("\n启动服务: http://localhost:8000")
    print("API 文档: http://localhost:8000/docs")
    subprocess.check_call([
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ])
