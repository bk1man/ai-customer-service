"""
LLM 客户端 - 智谱AI GLM-4-Flash
"""

import requests
from typing import Optional

# 凭证配置
ZHIPU_API_KEY = "6b533c89f08d4645beed47f7e0fb2c88.MTo7nAUVgT4KtBQw"
ZHIPU_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"

# 系统提示词
SYSTEM_PROMPT = """你是一个专业的AI客服助手，名为"图灵"。

你的职责：
1. 回答用户关于产品、服务的问题
2. 提供友好的客户服务
3. 如果不知道答案，诚实地告诉用户

回复要求：
- 语言简洁友好
- 使用中文回复
- 适当使用emoji
- 不要回复无关内容
- 如果问题涉及敏感话题，礼貌地转移话题

当前支持的业务：
- AI客服系统销售
- 建站服务
- Newsletter订阅服务
"""


class LLMClient:
    """智谱AI GLM-4-Flash 客户端"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or ZHIPU_API_KEY
        self.base_url = ZHIPU_BASE_URL
        self.model = "glm-4-flash"

    def chat(self, user_message: str, context: list = None) -> str:
        """发送对话请求到智谱AI"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        if context:
            messages.extend(context)

        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 500,
            "temperature": 0.7,
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=5,  # 微信超时5秒，快速响应
            )

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                print(f"LLM API error: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.Timeout:
            print("LLM API timeout")
            return None
        except Exception as e:
            print(f"LLM API exception: {e}")
            return None


# 全局单例
llm_client = LLMClient()


def get_llm_response(message: str, context: list = None) -> str:
    """获取LLM回复的便捷函数"""
    return llm_client.chat(message, context)
