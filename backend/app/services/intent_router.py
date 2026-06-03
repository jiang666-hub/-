"""
意图识别与智能路由服务
"""
import re
from typing import Tuple, Optional, List
from app.services.book_search import book_search_service
from app.models.schemas import Book

# RAG 服务延迟导入
_rag_service = None

def _get_rag_service():
    global _rag_service
    if _rag_service is None:
        try:
            from app.services.rag_service import get_rag_service as grs
            _rag_service = grs()
        except Exception:
            _rag_service = False  # 标记已尝试过，不再重试
    return _rag_service if _rag_service is not False else None


class IntentRouter:
    """
    根据用户输入识别意图，路由到对应处理模块：
    1. 图书查询：查找特定书籍的位置、库存
    2. 图书推荐：根据兴趣推荐书籍
    3. 规则问答：询问规章制度、开放时间等
    4. 闲聊：一般性对话
    """

    # 意图关键词模式
    INTENT_PATTERNS = {
        "book_query": [
            r"(找|查|搜|检索|在哪儿|在哪里|位置|在哪|几楼|索书号).*书",
            r"(有没有|有没有|有吗).*书",
            r"《.+》",
            r"借.*书",
            r"馆藏|库存|可借|在馆",
        ],
        "book_recommend": [
            r"推荐|建议|介绍|入门|适合.*学|零基础|新手",
            r"(有什么|哪些|有没有).*(好看|经典|有趣|值得)",
        ],
        "rule_query": [
            r"开放时间|几点开门|几点关门|几点开",
            r"借.*规则|借.*多久|借.*天|借.*本|怎么借|借书",
            r"逾期|罚款|滞纳金|赔偿|丢失|损坏",
            r"续借|还书|怎么还",
            r"座位|占座|自习|楼层",
            r"VPN|电子资源|数据库|知网|万方",
        ],
    }

    def classify(self, message: str) -> Tuple[str, float]:
        """分类用户意图（规则查询优先级最高）"""
        # 先检查规则查询（避免被 book_query 误匹配）
        for pattern in self.INTENT_PATTERNS["rule_query"]:
            if re.search(pattern, message):
                return "rule_query", 0.9

        for intent in ["book_query", "book_recommend"]:
            for pattern in self.INTENT_PATTERNS[intent]:
                if re.search(pattern, message):
                    return intent, 0.9
        return "general", 0.5

    def route(self, message: str, history: List[dict] = None, category: str = None):
        """
        路由并处理用户请求，返回结构化结果
        """
        intent, confidence = self.classify(message)

        if intent == "book_query":
            return self._handle_book_query(message)
        elif intent == "book_recommend":
            return self._handle_book_recommend(message, category)
        elif intent == "rule_query":
            return self._handle_rule_query(message)
        else:
            return self._handle_general(message, category)

    def _handle_book_query(self, message: str):
        """处理图书查询"""
        books = book_search_service.keyword_search(message, top_k=5)
        if not books:
            return {
                "answer": "抱歉，没有找到与「{}」相关的图书。你可以试试用书名、作者名或关键词搜索。".format(message),
                "books": [],
                "source": "book_query"
            }

        # 生成回答
        if len(books) == 1:
            book = books[0]
            answer = (
                f"找到了《{book.title}》：\n"
                f"- 作者：{book.author}\n"
                f"- 位置：{book.location}\n"
                f"- 索书号：{book.shelf_number}\n"
                f"- 状态：共 {book.stock} 本，可借 {book.available} 本\n"
                f"- 简介：{book.description}"
            )
        else:
            book_list = "\n".join([
                f"{i+1}. 《{b.title}》- {b.author} | {b.location} | 可借{b.available}本"
                for i, b in enumerate(books)
            ])
            answer = f"为您找到 {len(books)} 本相关图书：\n\n{book_list}\n\n想了解哪一本的详细信息？"

        return {
            "answer": answer,
            "books": [b.model_dump() for b in books],
            "source": "book_query"
        }

    def _handle_book_recommend(self, message: str, category: str = None):
        """处理图书推荐"""
        books = []

        # 尝试 RAG 语义搜索
        rag = _get_rag_service()
        if rag:
            try:
                semantic_results = rag.search_books(message, top_k=5)
                book_ids = [int(r[0]) for r in semantic_results]
                for bid in book_ids:
                    book = book_search_service.get_by_id(bid)
                    if book:
                        books.append(book)
            except Exception:
                pass

        if not books:
            books = book_search_service.keyword_search(message, top_k=5)

        # 如果指定了分类，筛选
        if category and category != "全部":
            filtered = [b for b in books if b.category == category]
            if not filtered:
                # 该分类下无结果，直接从全库中按分类取
                all_books = book_search_service.get_all_books()
                filtered = [b for b in all_books if b.category == category]
                import random
                random.shuffle(filtered)
                filtered = filtered[:5]
            books = filtered

        if not books:
            return {
                "answer": "暂时没有找到合适的推荐，请告诉我你感兴趣的领域，我来帮你找！",
                "books": [],
                "source": "book_recommend"
            }

        book_list = "\n".join([
            f"{i+1}. 《{b.title}》- {b.author} | {b.category} | {b.description[:30]}..."
            for i, b in enumerate(books)
        ])
        category_hint = f"【{category}】分类下，" if category else ""
        answer = f"根据你的需求，{category_hint}推荐以下几本书：\n\n{book_list}"

        return {
            "answer": answer,
            "books": [b.model_dump() for b in books],
            "source": "book_recommend"
        }

    def _load_rules_from_file(self, message: str):
        """从本地文件加载规章制度，按关键词匹配"""
        import os
        rules_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "data", "knowledge", "rules.md"
        )
        with open(rules_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 按关键词匹配章节
        sections = content.split("\n## ")
        rules = []
        keywords_map = {
            "开放时间": ["开放", "几点", "时间", "关门", "开门"],
            "借阅规则": ["借", "规则", "多久", "天", "本", "续借"],
            "违规处理": ["逾期", "罚款", "滞纳金", "赔偿", "丢失", "损坏", "占座", "喧哗"],
            "楼层分布": ["楼层", "几楼", "分布"],
            "电子资源": ["VPN", "电子", "数据库", "知网", "万方"],
        }

        matched_sections = set()
        for section in sections:
            section_lower = section.lower()
            for section_name, keywords in keywords_map.items():
                if section_name in section:
                    matched_sections.add(section_name)
                    for kw in keywords:
                        if kw in message:
                            rules.append(section.strip())
                            break
                    break

        # 如果关键词没匹配到，用逐字匹配兜底
        if not rules:
            for section in sections:
                for word in message:
                    if word in section:
                        rules.append(section.strip())
                        break

        # 去重
        seen = set()
        unique_rules = []
        for r in rules:
            key = r[:30]
            if key not in seen:
                seen.add(key)
                unique_rules.append(r)

        return unique_rules[:3]

    def _handle_rule_query(self, message: str):
        """处理规章制度查询"""
        rules = None

        # 尝试 RAG
        rag = _get_rag_service()
        if rag:
            try:
                rules = rag.search_rules(message, top_k=3)
            except Exception:
                rules = None

        # RAG 失败则降级到本地文件匹配
        if not rules:
            rules = self._load_rules_from_file(message)

        if not rules:
            return {
                "answer": "抱歉，我没有找到相关的规章制度信息。你可以咨询图书馆服务台（1楼总服务台）。",
                "books": [],
                "source": "rule_query"
            }

        answer = "根据图书馆规定：\n\n" + "\n\n".join(rules[:2])
        return {
            "answer": answer,
            "books": [],
            "source": "rule_query"
        }

    def _handle_general(self, message: str, category: str = None):
        """处理一般性问题——也尝试做关键词搜索"""
        # 先尝试关键词搜索
        books = book_search_service.keyword_search(message, top_k=5)

        # 如果指定了分类，筛选
        if category and category != "全部" and books:
            filtered = [b for b in books if b.category == category]
            if not filtered:
                all_books = book_search_service.get_all_books()
                filtered = [b for b in all_books if b.category == category]
                import random
                random.shuffle(filtered)
                filtered = filtered[:5]
            books = filtered

        if books:
            category_hint = f"【{category}】分类下，" if category else ""
            book_list = "\n".join([
                f"{i+1}. 《{b.title}》- {b.author} | {b.category} | {b.location} | 可借{b.available}本"
                for i, b in enumerate(books)
            ])
            return {
                "answer": f"搜索「{message}」，{category_hint}为您找到 {len(books)} 本相关图书：\n\n{book_list}\n\n想了解哪一本的详细信息？",
                "books": [b.model_dump() for b in books],
                "source": "book_query"
            }

        return {
            "answer": (
                "你好！我是图书馆智能助手，可以帮你：\n\n"
                "📚 **查书找书** - 比如「《三体》在哪儿？」\n"
                "🔍 **推荐图书** - 比如「推荐一本 Python 入门书」\n"
                "📋 **查询规则** - 比如「借书能借多久？」\n"
                "⏰ **开放时间** - 比如「图书馆几点关门？」\n\n"
                "请问有什么可以帮你的？"
            ),
            "books": [],
            "source": "general"
        }


intent_router = IntentRouter()
