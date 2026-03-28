"""
增强版知识库 - 支持多轮对话和语义匹配
Enhanced Knowledge Base with Context and Intent Recognition
"""

import re
from typing import Optional, List, Dict, Tuple


class EnhancedKnowledgeBase:
    """增强型知识库"""

    def __init__(self):
        self._qa_list: List[Dict] = []
        self._conversation_context: Dict[str, str] = {}  # 用户上下文
        self._init_comprehensive_knowledge()

    def _init_comprehensive_knowledge(self):
        """初始化全面知识库"""
        knowledge = [
            # 产品咨询
            {
                "intent": "product_inquiry",
                "question": "产品介绍",
                "answer": """🔥 我们的AI智能客服系统：

✅ 核心功能：
• 7×24小时在线，无需等待
• 语义理解，准确率95%+
• 支持多轮对话，记忆上下文
• 快速接入，5分钟上线
• 数据可视化，运营无忧

✅ 适用场景：
• 电商客服
• 售后咨询
• 产品问答
• 网站引流

📌 回复"价格"查看套餐详情
📌 回复"试用"申请免费体验""",
                "keywords": ["产品", "介绍", "功能", "特点", "是什么", "有什么用", "能做什么", "服务"],
                "follow_up": ["价格", "试用", "套餐"]
            },
            # 价格咨询
            {
                "intent": "price_inquiry",
                "question": "价格套餐",
                "answer": """💰 价格套餐：

🆓 免费版
• 每月100次对话
• 基础知识库
• 单渠道接入

💎 专业版 ¥99/月
• 无限对话
• 高级知识库
• 多渠道接入
• 数据分析
• 优先支持

🏢 企业版 ¥399/月
• 私有化部署
• 定制开发
• 专属客服
• SLA保障

📌 回复"试用"免费体验""",
                "keywords": ["价格", "多少钱", "收费", "费用", "套餐", "月费", "年费", "付费", "免费"],
                "follow_up": ["试用", "优惠", "折扣"]
            },
            # 试用咨询
            {
                "intent": "trial_inquiry",
                "question": "免费试用",
                "answer": """🎁 申请免费试用：

1. 关注公众号
2. 回复"试用"+您的邮箱
3. 我们会在24小时内发送体验账号

📧 或者直接联系人工客服：
• 微信：AI_Service
• 邮箱：support@ai-service.com

⏰ 体验期：7天
💡 无需信用卡""",
                "keywords": ["试用", "体验", "申请", "开通", "注册", "开始使用", "如何开始"],
                "follow_up": ["联系客服", "邮箱"]
            },
            # 工作时间
            {
                "intent": "working_hours",
                "question": "工作时间",
                "answer": """⏰ 我们的服务时间：

📅 工作日
周一至周五：9:00 - 22:00

📅 周末
周六：10:00 - 18:00
周日：14:00 - 20:00

🌙 夜间留言
非工作时间请留言，我们会在次日9:00前回复

💬 紧急问题请联系微信客服""",
                "keywords": ["工作时间", "上班", "营业", "几点", "开门", "营业时间", "客服时间", "在线时间"],
                "follow_up": ["联系客服", "微信"]
            },
            # 联系方式
            {
                "intent": "contact_info",
                "question": "联系方式",
                "answer": """📞 联系我们：

💬 微信客服（推荐）
搜索添加：AI_Service

📧 邮箱
support@ai-service.com

📱 电话
400-888-8888

⏰ 服务时间
工作日 9:00-22:00

🔥 紧急问题推荐微信，响应更快！""",
                "keywords": ["联系", "电话", "邮箱", "微信", "怎么联系", "客服", "人工", "有人吗"],
                "follow_up": []
            },
            # 退款政策
            {
                "intent": "refund_policy",
                "question": "退款政策",
                "answer": """💸 退款政策：

✅ 7天内无理由退款
• 无需说明原因
• 全额退款到原支付渠道

✅ 质量问题
• 提供证据后全额退款
• 24小时内处理

⚠️ 退款流程
1. 联系客服申请
2. 审核通过后1-3个工作日到账

📌 如有疑问请回复"联系客服">""",
                "keywords": ["退款", "退钱", "取消", "退款政策", "钱", "费用", "投诉", "不满"],
                "follow_up": ["联系客服"]
            },
            # 发票问题
            {
                "intent": "invoice_inquiry",
                "question": "发票问题",
                "answer": """📄 发票开具：

✅ 支持类型
• 增值税普通发票
• 增值税专用发票

✅ 所需信息
• 公司名称
• 统一社会信用代码
• 开户行及账号（如需专票）

⏰ 开具时间
付款后1-3个工作日

📧 发送方式
电子发票发送至邮箱
纸质发票快递到家

📌 回复"发票"+您的邮箱+公司信息""",
                "keywords": ["发票", "收据", "报销", "开票", "增值税"],
                "follow_up": []
            },
            # 技术支持
            {
                "intent": "tech_support",
                "question": "技术支持",
                "answer": """🔧 技术支持：

📖 文档中心
docs.ai-service.com

💬 技术支持群
• 专属技术客服1对1
• 7×24小时响应
• 远程协助

🐛 提交问题
• 描述问题现象
• 提供截图/日志
• 留下联系方式

⏰ 响应时间
• 紧急：2小时内
• 一般：24小时内""",
                "keywords": ["技术", "支持", "帮助", "问题", "故障", "报错", "不会", "怎么弄", "帮帮我", "解决"],
                "follow_up": ["文档", "技术支持群"]
            },
            # 合作伙伴
            {
                "intent": "partner_inquiry",
                "question": "合作伙伴",
                "answer": """🤝 合作伙伴招募：

✅ 合作模式
• 代理商：返佣20-40%
• 渠道商：专属折扣
• 集成商：技术对接支持

✅ 支持政策
• 产品培训
• 营销物料
• 技术支持
• 专属客服

📊 合作案例
已服务500+企业客户

📌 回复"合作"+您的公司信息""",
                "keywords": ["合作", "代理", "渠道", "加盟", "伙伴", "代理", "分销", "赚"],
                "follow_up": []
            },
            # 默认/未知问题
            {
                "intent": "fallback",
                "question": "未知问题",
                "answer": None,  # 特殊处理
                "keywords": [],
                "follow_up": []
            }
        ]

        for item in knowledge:
            self.add_qa(item["question"], item["answer"], item["keywords"], item.get("intent"), item.get("follow_up"))

    def add_qa(self, question: str, answer: str, keywords: List[str] = None, intent: str = None, follow_up: List[str] = None):
        """添加问答对"""
        if keywords is None:
            keywords = []
        if intent is None:
            intent = "general"
        if follow_up is None:
            follow_up = []

        if not keywords:
            keywords = self._extract_keywords(question)

        self._qa_list.append({
            "question": question,
            "answer": answer,
            "keywords": keywords,
            "intent": intent,
            "follow_up": follow_up
        })

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        stop_words = {"的", "了", "是", "在", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这", "请", "您", "我们", "吗", "呢", "吧", "啊"}
        words = re.findall(r'\w+', text)
        return [w for w in words if w not in stop_words and len(w) > 1]

    def recognize_intent(self, query: str) -> Tuple[str, float]:
        """识别用户意图"""
        query_lower = query.lower()

        best_intent = "fallback"
        best_score = 0

        for item in self._qa_list:
            if item["intent"] == "fallback":
                continue

            # 关键词匹配打分
            for keyword in item["keywords"]:
                if keyword.lower() in query_lower:
                    score = len(keyword) * 2  # 关键词匹配权重
                    if score > best_score:
                        best_score = score
                        best_intent = item["intent"]

            # 问题包含匹配
            if item["question"].lower() in query_lower:
                return item["intent"], 100.0

        return best_intent, min(best_score, 100.0)

    def search(self, query: str, user_id: str = None) -> Optional[Dict]:
        """搜索匹配的回答"""
        intent, confidence = self.recognize_intent(query)

        for item in self._qa_list:
            if item["intent"] == intent:
                result = {
                    "answer": item["answer"],
                    "intent": intent,
                    "confidence": confidence,
                    "follow_up": item.get("follow_up", [])
                }

                # 保存上下文
                if user_id:
                    self._conversation_context[user_id] = intent

                return result

        return None

    def get_context_response(self, user_id: str, query: str) -> Dict:
        """获取带上下文的回复"""
        # 先搜索当前问题
        result = self.search(query, user_id)

        if result:
            return result

        # 尝试上下文理解
        last_intent = self._conversation_context.get(user_id)

        # 如果用户继续追问，尝试在上下文中回答
        if last_intent:
            for item in self._qa_list:
                if item["intent"] == last_intent:
                    return {
                        "answer": f"{item['answer']}\n\n💬 您还可以回复：\n" + "\n".join([f"• {f}" for f in item.get("follow_up", [])]),
                        "intent": last_intent,
                        "confidence": 70.0,
                        "follow_up": item.get("follow_up", [])
                    }

        # 兜底回复
        return {
            "answer": """🤔 抱歉，我还在学习中...

您可以尝试：
• 简单描述您的问题
• 回复数字选择：

1️⃣ 产品介绍
2️⃣ 价格咨询
3️⃣ 免费试用
4️⃣ 联系我们
5️⃣ 技术支持

或者联系人工客服💬""",
            "intent": "fallback",
            "confidence": 0.0,
            "follow_up": ["产品介绍", "价格", "试用", "联系"]
        }

    def count(self) -> int:
        """返回知识库条目数量"""
        return len([item for item in self._qa_list if item["intent"] != "fallback"])
