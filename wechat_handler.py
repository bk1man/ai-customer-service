"""
微信公众号消息处理器 - 接入LLM大模型 + AI建站
"""

import xml.etree.ElementTree as ET
import time
import hashlib
import threading
import requests
from knowledge_base import EnhancedKnowledgeBase
from llm_client import LLMClient
from website_generator import WebsiteGenerator
from wechat_push import get_access_token

llm_client = LLMClient()
website_generator = WebsiteGenerator()


class WeChatHandler:
    def __init__(self, knowledge_base: EnhancedKnowledgeBase):
        self.kb = knowledge_base
        self._website_pending = {}
        self._website_modifying = {}
        self._conversation_history = {}  # open_id -> list of (role, content)

    def process_message(self, xml_data: bytes) -> str:
        try:
            root = ET.fromstring(xml_data.decode("utf-8"))
            msg_type = root.find("MsgType").text
            from_user = root.find("FromUserName").text
            to_user = root.find("ToUserName").text

            if msg_type == "text":
                content = root.find("Content").text or ""
                return self.handle_text(from_user, to_user, content, from_user)
            elif msg_type == "event":
                event = root.find("Event").text
                return self.handle_event(from_user, to_user, event)
            else:
                return self._make_text_reply(from_user, to_user, "收到，客服正在处理中...")
        except Exception as e:
            print(f"处理消息异常: {e}")
            return ""

    def handle_text(self, from_user: str, to_user: str, content: str, user_id: str) -> str:
        content = content.strip()
        # 清理3分钟不活跃用户的记忆
        self._cleanup_stale_conversations(from_user)
        if not content:
            return self._make_text_reply(from_user, to_user, "请输入您的问题，我会尽力为您解答 😊")

        # 修改网站意图
        modify_keywords = ["换个颜色", "改标题", "改内容", "加产品", "重新生成", "修改网站", "改一下", "调整"]
        if any(kw in content for kw in modify_keywords) and from_user in self._website_modifying:
            prompt = "好的！请直接告诉我您想要的修改，比如：'把色调改成蓝色系' 或 '标题改成慢时光咖啡'，我会立刻帮您调整！"
            return self._make_text_reply(from_user, to_user, prompt)

        # 建站意图检测
        website_keywords = ["建站", "网站", "做网站", "建落地页", "做个网站", "网页", "落地页", "我想做个", "帮我建", "建个网站"]
        if any(kw in content for kw in website_keywords):
            if from_user in self._website_pending:
                desc = self._website_pending.pop(from_user) + " " + content
                self._website_modifying[from_user] = {"description": desc}
                return self._start_website_generation(from_user, to_user, desc)
            else:
                self._website_pending[from_user] = content
                prompt = "好的，我来帮您建站！\n\n请告诉我：\n① 您的店名/品牌名是什么？\n② 主要产品或服务是什么？\n③ 想要的风格？（如：简约、复古、时尚）\n\n直接回复即可，例如：'慢时光手冲咖啡店，主打手冲和甜点，风格复古文艺'"
                return self._make_text_reply(from_user, to_user, prompt)

        # 二次信息（建站流程中）
        if from_user in self._website_pending:
            desc = self._website_pending.pop(from_user) + " " + content
            self._website_modifying[from_user] = {"description": desc}
            return self._start_website_generation(from_user, to_user, desc)

        # 通用问候
        greetings = ["你好", "您好", "hi", "hello", "嗨", "hey", "在吗", "在么", "在不在"]
        if content.lower() in [g.lower() for g in greetings]:
            return self._make_text_reply(from_user, to_user, self._get_welcome_message())

        # 数字快捷回复
        quick_replies = {
            "1": ("产品介绍", "product_inquiry"),
            "2": ("价格套餐", "price_inquiry"),
            "3": ("免费试用", "trial_inquiry"),
            "4": ("联系我们", "contact_info"),
            "5": ("技术支持", "tech_support"),
            "6": ("AI建站", "website_building"),
        }
        if content in quick_replies:
            intent_name, intent_key = quick_replies[content]
            if intent_key == "website_building":
                self._website_pending[from_user] = ""
                prompt = "欢迎使用AI建站服务！\n\n请描述您想建的网站，例如：\n'瑜伽馆，主打私教课和团课，风格清新自然'\n\n我们会在30秒内为您生成专属落地页！"
                return self._make_text_reply(from_user, to_user, prompt)
            result = self.kb.search(intent_name, user_id)
            if result and result["answer"]:
                return self._make_text_reply(from_user, to_user, result["answer"])
            return self._make_text_reply(from_user, to_user, f"您选择了{intent_name}，请稍等...")

        # 知识库匹配
        result = self.kb.get_context_response(user_id, content)
        if result and result["answer"] and result["confidence"] >= 70:
            answer = result["answer"]
            follow_ups = result.get("follow_up", [])
            if follow_ups:
                text = "📌 您还可以回复：\n"
                for i, f in enumerate(follow_ups[:3], 1):
                    text += f"{i}. {f}\n"
                text += "6. 🎨 AI建站"
                answer = f"{answer}\n\n{text}"
            return self._make_text_reply(from_user, to_user, answer)

        # LLM兜底（带对话历史记忆）
        history = self._conversation_history.get(from_user, [])
        history.append({"role": "user", "content": content})
        if len(history) > 10:
            history = history[-10:]
        self._conversation_history[from_user] = history
        print(f"调用LLM处理: {content} (history={len(history)} msgs)")
        llm_response = llm_client.chat(content, history)
        if llm_response:
            return self._make_text_reply(from_user, to_user, llm_response)

        return self._make_text_reply(from_user, to_user, self._get_fallback_message())

    def _start_website_generation(self, from_user: str, to_user: str, description: str) -> str:
        threading.Thread(target=self._generate_website_async, args=(from_user, description), daemon=True).start()
        return self._make_text_reply(from_user, to_user,
            "⏳ 收到！正在为您生成专属网站，预计30秒内完成...\n生成完成后我会第一时间通知您！🔔")

    def _generate_website_async(self, from_user: str, description: str):
        try:
            url = website_generator.generate(description)
            if url:
                success_msg = (
                    "🎉 您的专属网站已生成！\n\n"
                    "🔗 访问链接：" + url + "\n\n"
                    "✨ 如需修改，请对我说：\n"
                    "• '换个颜色' - 更换主题色\n"
                    "• '改个标题' - 修改主标题\n"
                    "• '加个产品' - 添加产品展示\n"
                    "• '重新生成' - 从头来过\n\n"
                    "或者直接描述您想要的修改！"
                )
                self._send_wechat_message(from_user, success_msg)
            else:
                self._send_wechat_message(from_user,
                    "😔 抱歉，网站生成失败了。请说'重新生成'或联系人工客服。")
        except Exception as e:
            print(f"网站生成异常: {e}")
            self._send_wechat_message(from_user,
                "😔 抱歉，网站生成出现异常，请联系人工客服处理。")

    def _send_wechat_message(self, to_user: str, content: str):
        try:
            token = get_access_token()
            if not token:
                print("[WeChat] cannot get token")
                return
            api_url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={token}"
            import json
            payload = {"touser": to_user, "msgtype": "text", "text": {"content": content}}
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            resp = requests.post(api_url, data=body, headers={"Content-Type": "application/json; charset=utf-8"}, timeout=10)
            print(f"[WeChat] send result: {resp.json()}")
        except Exception as e:
            print(f"[WeChat] send failed: {e}")

    def handle_event(self, from_user: str, to_user: str, event: str) -> str:
        if event == "subscribe":
            return self._make_text_reply(from_user, to_user, self._get_welcome_message())
        elif event == "unsubscribe":
            return ""
        return ""

    def _cleanup_stale_conversations(self, current_user: str):
        import time
        cutoff = time.time() - 180  # 3分钟前
        stale = [uid for uid, last_time in getattr(self, '_last_active', {}).items() if last_time < cutoff]
        for uid in stale:
            self._conversation_history.pop(uid, None)
            self._website_pending.pop(uid, None)
            self._website_modifying.pop(uid, None)
        # 更新当前用户活跃时间
        if not hasattr(self, '_last_active'):
            self._last_active = {}
        self._last_active[current_user] = time.time()

    def _get_welcome_message(self) -> str:
        return ("👋 欢迎关注！\n\n"
                "我是您的AI智能助手，可以帮您：\n\n"
                "🔹 产品咨询\n"
                "🔹 价格了解\n"
                "🔹 免费试用\n"
                "🔹 技术支持\n"
                "🔹 🎨 AI建站 - 30秒生成专属落地页！\n\n"
                "请直接输入您的问题，我会尽力为您解答！\n\n"
                "💡 快捷入口：\n"
                "• 回复\"1\" - 产品介绍\n"
                "• 回复\"2\" - 价格套餐\n"
                "• 回复\"3\" - 免费试用\n"
                "• 回复\"4\" - 联系我们\n"
                "• 回复\"6\" - 🎨 AI建站")

    def _get_fallback_message(self) -> str:
        return ("🤔 抱歉，我还在学习中...\n\n"
                "您可以尝试：\n"
                "• 简单描述您的问题\n"
                "• 回复数字选择：\n\n"
                "1️⃣ 产品介绍\n"
                "2️⃣ 价格咨询\n"
                "3️⃣ 免费试用\n"
                "4️⃣ 联系我们\n"
                "5️⃣ 技术支持\n"
                "6️⃣ 🎨 AI建站\n\n"
                "或者联系人工客服💬")

    def _make_text_reply(self, from_user: str, to_user: str, content: str) -> str:
        return (f"<xml>\n"
                f"<ToUserName><![CDATA[{from_user}]]></ToUserName>\n"
                f"<FromUserName><![CDATA[{to_user}]]></FromUserName>\n"
                f"<CreateTime>{int(time.time())}</CreateTime>\n"
                f"<MsgType><![CDATA[text]]></MsgType>\n"
                f"<Content><![CDATA[{content}]]></Content>\n"
                f"</xml>")
