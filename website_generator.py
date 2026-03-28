"""
AI 网站生成器 - 根据用户需求生成临时落地页
"""

import uuid
import os
import requests
import re
import json
from typing import Optional

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{hero_title}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; }
        .gradient-hero { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .glass { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); }
        .float { animation: float 3s ease-in-out infinite; }
        @keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-10px)} }
    </style>
</head>
<body class="bg-gray-900 text-white">
    <nav class="fixed top-0 w-full bg-gray-900/80 backdrop-blur-md z-50 border-b border-gray-800">
        <div class="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
            <div class="text-xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">{{nav_title}}</div>
            <a href="#contact" class="px-5 py-2 bg-purple-600 hover:bg-purple-700 rounded-full text-sm font-medium transition">联系我们</a>
        </div>
    </nav>
    <section class="gradient-hero min-h-screen flex items-center justify-center text-center px-6 pt-20">
        <div class="max-w-3xl">
            <h1 class="text-5xl md:text-6xl font-bold mb-6 leading-tight">{{hero_title}}</h1>
            <p class="text-xl text-gray-200 mb-8">{{hero_subtitle}}</p>
            <div class="flex flex-col sm:flex-row gap-4 justify-center">
                <a href="#features" class="px-8 py-4 bg-white text-purple-700 font-bold rounded-full hover:bg-gray-100 transition float">了解更多</a>
                <a href="#contact" class="px-8 py-4 glass text-white font-bold rounded-full hover:bg-white/20 transition">立即体验</a>
            </div>
        </div>
    </section>
    <section id="features" class="py-24 bg-gray-800">
        <div class="max-w-6xl mx-auto px-6">
            <h2 class="text-4xl font-bold text-center mb-16">{{features_title}}</h2>
            <div class="grid md:grid-cols-3 gap-8">{{features_cards}}</div>
        </div>
    </section>
    <section class="py-24 bg-gray-900">
        <div class="max-w-4xl mx-auto px-6 text-center">
            <h2 class="text-4xl font-bold mb-8">{{about_title}}</h2>
            <p class="text-xl text-gray-400 leading-relaxed">{{about_content}}</p>
        </div>
    </section>
    <section id="contact" class="py-24 gradient-hero">
        <div class="max-w-2xl mx-auto px-6 text-center">
            <h2 class="text-4xl font-bold mb-6">{{contact_title}}</h2>
            <p class="text-xl text-gray-200 mb-10">{{contact_subtitle}}</p>
            <div class="glass rounded-2xl p-8">
                <p class="text-2xl font-bold mb-4">联系方式</p>
                <p class="text-lg">微信咨询：AI_Service</p>
                <p class="text-lg">邮箱：contact@example.com</p>
            </div>
        </div>
    </section>
    <footer class="bg-gray-900 py-8 border-t border-gray-800 text-center text-gray-500 text-sm">
        <p>© 2026 {{footer_text}}. All rights reserved.</p>
    </footer>
</body>
</html>"""

FEATURE_CARD = """<div class="bg-gray-700 rounded-2xl p-8 hover:bg-gray-600 transition"><div class="text-4xl mb-4">{{icon}}</div><h3 class="text-xl font-bold mb-3">{{card_title}}</h3><p class="text-gray-400">{{card_desc}}</p></div>"""

SYSTEM_PROMPT = """你是一个专业的落地页HTML生成助手。根据用户需求，生成一个精美的单页落地页配置。

请严格按以下JSON格式返回（不要加任何其他内容，只返回JSON）：
{"nav_title":"名称","hero_title":"标题","hero_subtitle":"副标题","features_title":"特色标题","features":[{"icon":"图标(必须是单个emoji)","card_title":"标题","card_desc":"描述"},{"icon":"图标(必须是单个emoji)","card_title":"标题","card_desc":"描述"},{"icon":"图标(必须是单个emoji)","card_title":"标题","card_desc":"描述"}],"about_title":"关于我们标题","about_content":"关于我们内容","contact_title":"联系我们标题","contact_subtitle":"联系副标题","footer_text":"页脚公司名"}"""


class WebsiteGenerator:
    def __init__(self):
        self.api_key = "6b533c89f08d4645beed47f7e0fb2c88.MTo7nAUVgT4KtBQw"
        self.base_url = "https://open.bigmodel.cn/api/paas/v4"

    def generate(self, user_description: str) -> Optional[str]:
        print(f"[WebsiteGenerator] generating: {user_description}")
        config = self._call_llm(user_description)
        if not config:
            return None
        html = self._render_html(config)
        filename = f"{uuid.uuid4().hex[:8]}.html"
        filepath = f"/var/www/newsletter/temp/{filename}"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        url = f"https://ysywlkj.xyz/temp/{filename}"
        print(f"[WebsiteGenerator] done: {url}")
        return url

    def _call_llm(self, description: str) -> Optional[dict]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "glm-4-flash",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"请为以下业务生成落地页配置：{description}"}
            ],
            "max_tokens": 600,
            "temperature": 0.8,
        }
        try:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers, json=payload, timeout=30
            )
            if resp.status_code == 200:
                raw = resp.json()["choices"][0]["message"]["content"]
                config = self._extract_json(raw)
                if config:
                    return config
            else:
                print(f"LLM error: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"LLM exception: {e}")
        return None

    def _extract_json(self, text: str) -> Optional[dict]:
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1])
        text = text.strip("`").strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(text[start:end])
                except:
                    pass
        return None

    def _render_html(self, config: dict) -> str:
        cards_html = ""
        for f in config.get("features", []):
            icon = f.get("icon", "X")
            if len(icon) > 3:
                icon = "X"
            cards_html += FEATURE_CARD \
                .replace("{{icon}}", icon) \
                .replace("{{card_title}}", f.get("card_title", "")) \
                .replace("{{card_desc}}", f.get("card_desc", ""))
        return TEMPLATE \
            .replace("{{nav_title}}", config.get("nav_title", "")) \
            .replace("{{hero_title}}", config.get("hero_title", "")) \
            .replace("{{hero_subtitle}}", config.get("hero_subtitle", "")) \
            .replace("{{features_title}}", config.get("features_title", "")) \
            .replace("{{features_cards}}", cards_html) \
            .replace("{{about_title}}", config.get("about_title", "")) \
            .replace("{{about_content}}", config.get("about_content", "")) \
            .replace("{{contact_title}}", config.get("contact_title", "")) \
            .replace("{{contact_subtitle}}", config.get("contact_subtitle", "")) \
            .replace("{{footer_text}}", config.get("footer_text", ""))


website_generator = WebsiteGenerator()
