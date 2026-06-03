# 📚 图书馆图文智能体

支持图书检索、分类推荐、规章制度问答的智能助手。

## 技术栈

- **后端**: FastAPI + ChromaDB + Sentence-Transformers
- **前端**: Vue 3 + Vite
- **部署**: Render (免费)

## 本地运行

```bash
# 后端
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

## 一键部署

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

将项目推送到 GitHub 后，在 Render 中连接仓库即可自动部署。
