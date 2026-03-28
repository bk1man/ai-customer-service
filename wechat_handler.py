"""
微信公众号消息处理器
WeChat Message Handler
"""

import xml.etree.ElementTree as ET
import time
import hashlib
from knowledge_base import KnowledgeBase


class WeChatHandler:
    """处理微信消息和回复"""

    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base

    def process_message(self, xml_data: bytes) -> str:
        """处理收到的微信消息"""
        try:
            root = ET.fromstring(xml_data.decode("utf-8"))
            msg_type = root.find("MsgType").text
            from_user = root.find("FromUserName").text
            to_user = root.find("ToUserName").text

            # 根据消息类型处理
            if msg_type == "text":
                content = root.find("Content").text
                return self.handle_text(from_user, to_user, content)
            elif msg_type == "event":
                event = root.find("Event").text
                return self.handle_event(from_user, to_user, event)
            else:
                # 其他消息类型暂不处理
                return self._make_text_reply(from_user, to_user, "收到，客服正在处理中...")
        except Exception as e:
            print(f"处理消息异常: {e}")
            return ""

    def handle_text(self, from_user: str, to_user: str, content: str) -> str:
        """处理用户文本消息"""
        # 先尝试知识库匹配
        answer = self.kb.search(content)
        if answer:
            return self._make_text_reply(from_user, to_user, answer)

        # TODO: 接入LLM API
        # answer = await self.call_llm(content)
        # 伪代码示例:
        # def call_llm(user_message: str) -> str:
        #     """
        #     调用大语言模型接口
        #     payload = {
        #         "model": "gpt-3.5-turbo",
        #         "messages": [{"role": "user", "content": user_message}]
        #     }
        #     response = requests.post(
        #         "https://api.openai.com/v1/chat/completions",
        #         headers={"Authorization": f"Bearer {API_KEY}"},
        #         json=payload
        #     )
        #     return response.json()["choices"][0]["message"]["content"]
        # """

        # 默认回复
        default_reply = (
            "感谢您的留言！\n"
            "我是一个AI客服助手，目前还在学习阶段。\n"
            "常见问题请回复对应数字：\n"
            "1. 工作时间\n"
            "2. 联系方式\n"
            "3. 产品介绍\n"
            "或直接描述您的问题，我会尽力回答。"
        )
        return self._make_text_reply(from_user, to_user, default_reply)

    def handle_event(self, from_user: str, to_user: str, event: str) -> str:
        """处理事件消息"""
        if event == "subscribe":
            # 用户关注事件
            welcome_msg = (
                "👋 欢迎关注！\n\n"
                "我是您的AI客服助手，可以为您提供：\n"
                "• 产品咨询\n"
                "• 常见问题解答\n"
                "• 售后服务支持\n\n"
                "请直接发送您的问题，我会尽快回复！"
            )
            return self._make_text_reply(from_user, to_user, welcome_msg)
        elif event == "unsubscribe":
            # 用户取消关注
            return ""
        else:
            return ""

    def _make_text_reply(self, from_user: str, to_user: str, content: str) -> str:
        """生成文本回复XML"""
        return f"""<xml>
<ToUserName><![CDATA[{from_user}]]></ToUserName>
<FromUserName><![CDATA[{to_user}]]></FromUserName>
<CreateTime>{int(time.time())}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{content}]]></Content>
</xml>"""

    def _make_image_reply(self, from_user: str, to_user: str, media_id: str) -> str:
        """生成图片回复XML"""
        return f"""<xml>
<ToUserName><![CDATA[{from_user}]]></ToUserName>
<FromUserName><![CDATA[{to_user}]]></FromUserName>
<CreateTime>{int(time.time())}</CreateTime>
<MsgType><![CDATA[image]]></MsgType>
<Image>
<MediaId><![CDATA[{media_id}]]></MediaId>
</Image>
</xml>"""
