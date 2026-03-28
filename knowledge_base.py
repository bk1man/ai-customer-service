"""
知识库模块
Knowledge Base for Q&A Matching
"""

import re
from typing import Optional, List, Dict


class KnowledgeBase:
    """简单的知识库实现，支持关键词匹配"""

    def __init__(self):
        self._qa_list: List[Dict[str, any]] = []
        self._init_default_knowledge()

    def _init_default_knowledge(self):
        """初始化默认知识库"""
        default_knowledge = [
            {
                "question": "工作时间",
                "answer": "我们的工作时间：\n周一至周五 9:00-18:00\n周六 10:00-16:00\n周日休息",
                "keywords": ["工作时间", "上班", "营业", "几点", "开门"]
            },
            {
                "question": "联系方式",
                "answer": "联系我们：\n📞 电话：400-888-8888\n📧 邮箱：support@example.com\n💬 微信：AI_Service",
                "keywords": ["联系", "电话", "邮箱", "微信", "怎么联系"]
            },
            {
                "question": "产品价格",
                "answer": "产品价格说明：\n基础版：免费\n专业版：99元/月\n企业版：399元/月\n如有疑问请告诉我们您的需求！",
                "keywords": ["价格", "多少钱", "收费", "费用", "套餐"]
            },
            {
                "question": "产品介绍",
                "answer": "🔥 我们的产品特点：\n• 智能客服7x24在线\n• 支持多轮对话\n• 快速接入，简单易用\n• 安全稳定，数据加密\n\n回复\"价格\"了解套餐详情",
                "keywords": ["产品", "介绍", "功能", "特点", "是什么"]
            },
            {
                "question": "使用方法",
                "answer": "使用方法：\n1. 注册账号\n2. 接入SDK\n3. 配置知识库\n4. 上线运营\n\n需要详细文档请回复\"文档\"",
                "keywords": ["使用", "怎么用", "教程", "接入", "文档", "帮助"]
            },
            {
                "question": "退款政策",
                "answer": "退款政策：\n• 7天内无理由退款\n• 质量问题全额退款\n• 超过7天按剩余天数折算\n\n如有退款需求请联系客服",
                "keywords": ["退款", "退钱", "取消", "退款政策"]
            }
        ]
        for item in default_knowledge:
            self.add_qa(item["question"], item["answer"], item["keywords"])

    def add_qa(self, question: str, answer: str, keywords: List[str] = None):
        """添加问答对"""
        if keywords is None:
            keywords = []
        # 从问题中提取关键词
        if not keywords:
            keywords = self._extract_keywords(question)
        self._qa_list.append({
            "question": question,
            "answer": answer,
            "keywords": keywords
        })

    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        # 简单实现：去除常见停用词
        stop_words = {"的", "了", "是", "在", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这"}
        words = re.findall(r'\w+', text)
        return [w for w in words if w not in stop_words and len(w) > 1]

    def search(self, query: str) -> Optional[str]:
        """搜索匹配的回答"""
        query_lower = query.lower()

        best_match = None
        best_score = 0

        for item in self._qa_list:
            # 检查关键词匹配
            for keyword in item["keywords"]:
                if keyword.lower() in query_lower:
                    score = len(keyword)
                    if score > best_score:
                        best_score = score
                        best_match = item["answer"]
                    break

            # 检查问题匹配
            if item["question"].lower() in query_lower:
                return item["answer"]

        return best_match

    def list_all(self) -> List[Dict]:
        """列出所有问答"""
        return [{"question": item["question"], "answer": item["answer"]} for item in self._qa_list]

    def count(self) -> int:
        """返回知识库条目数量"""
        return len(self._qa_list)
