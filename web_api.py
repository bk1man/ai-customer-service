"""

import os
os.environ["WERKZEUG_DEBUG_PIN"] = "off"
AI 建站 Web API - 独立服务
提供网页端网站生成接口
"""

import uuid
import os
import json
import time
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)
app.config["TRUSTED_HOSTS"] = ["ysywlkj.xyz", "www.ysywlkj.xyz", "localhost", "127.0.0.1"]
app.config["SERVER_NAME"] = None
app.config["APPLICATION_ROOT"] = "/"

# 配置
ZHIPU_API_KEY = "6b533c89f08d4645beed47f7e0fb2c88.MTo7nAUVgT4KtBQw"
ZHIPU_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
OUTPUT_DIR = "/var/www/ai-website/temp"
BASE_URL = "https://ysywlkj.xyz/temp"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 多模板系统
TEMPLATES = {
    "modern": {
        "name": "现代商务",
        "desc": "渐变背景 + 玻璃态效果，适合科技公司",
        "css": "body{font-family:'Inter','PingFang SC',sans-serif;margin:0}*{box-sizing:border-box}.gradient{background:linear-gradient(135deg,#667eea,#764ba2)}.glass{background:rgba(255,255,255,.1);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,.2);border-radius:16px}"
    },
    "minimal": {
        "name": "极简白",
        "desc": "白色背景 + 简洁排版，适合服务业",
        "css": "body{font-family:'Inter','PingFang SC',sans-serif;margin:0;background:#fff;color:#333}*{box-sizing:border-box}"
    },
    "dark": {
        "name": "暗黑科技",
        "desc": "深色背景 + 霓虹色，适合科技/游戏",
        "css": "body{font-family:'Inter','PingFang SC',sans-serif;margin:0;background:#0a0a0a;color:#fff}*{box-sizing:border-box}.neon{color:#00ff88;text-shadow:0 0 10px #00ff88}"
    }
}

SYSTEM_PROMPT = """你是一个专业的落地页生成助手。根据用户描述，生成一个精美的单页网站配置。

严格按以下JSON格式返回（只返回JSON，不要其他内容）：
{
  "title": "页面标题",
  "hero_title": "主标题（大字）",
  "hero_subtitle": "副标题",
  "company": "公司/品牌名",
  "features": [
    {"icon": "emoji", "title": "特色标题", "desc": "特色描述"},
    {"icon": "emoji", "title": "特色标题", "desc": "特色描述"},
    {"icon": "emoji", "title": "特色标题", "desc": "特色描述"}
  ],
  "about": "关于我们内容（2-3句话）",
  "contact_phone": "联系电话或微信号",
  "contact_email": "邮箱（可选）",
  "cta_text": "行动号召文字"
}

要求：
- 内容专业、有说服力
- emoji图标要合适（1-2个字符）
- 标题要吸引人
- 根据业务类型调整语气"""


def generate_html(config, template_key="modern"):
    """根据配置和模板生成HTML"""
    template = TEMPLATES.get(template_key, TEMPLATES["modern"])
    
    features_html = ""
    for f in config.get("features", []):
        icon = f.get("icon", "X")
        if len(icon) > 3:
            icon = "X"
        features_html += f'''<div style="background:#f8f9fa;padding:30px;border-radius:16px;text-align:center;transition:transform 0.3s" onmouseover="this.style.transform='translateY(-5px)'" onmouseout="this.style.transform='none'">
            <div style="font-size:48px;margin-bottom:16px">{icon}</div>
            <h3 style="font-size:20px;font-weight:700;margin-bottom:10px;color:#1a1a2e">{f.get("title", "")}</h3>
            <p style="color:#666;line-height:1.6">{f.get("desc", "")}</p>
        </div>'''

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config.get("title", "AI建站")}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        {template["css"]}
        a {{ text-decoration: none; }}
        .container {{ max-width: 1100px; margin: 0 auto; padding: 0 24px; }}
        .btn {{ display: inline-block; padding: 14px 36px; border-radius: 50px; font-weight: 700; font-size: 16px; transition: all 0.3s; cursor: pointer; border: none; }}
        .btn-primary {{ background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; }}
        .btn-primary:hover {{ transform: scale(1.05); box-shadow: 0 8px 30px rgba(102,126,234,0.4); }}
        .btn-outline {{ background: transparent; border: 2px solid rgba(255,255,255,0.3); color: #fff; }}
        .btn-outline:hover {{ border-color: #fff; }}
        .features-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; }}
        .section {{ padding: 80px 0; }}
        @media(max-width:768px) {{ .features-grid {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>
    <!-- Nav -->
    <nav style="position:fixed;top:0;width:100%;z-index:100;padding:16px 0;background:rgba(0,0,0,0.3);backdrop-filter:blur(10px)">
        <div class="container" style="display:flex;justify-content:space-between;align-items:center">
            <div style="font-size:20px;font-weight:800">{config.get("company", "AI建站")}</div>
            <a href="#contact" class="btn btn-primary" style="padding:10px 24px;font-size:14px">联系我们</a>
        </div>
    </nav>

    <!-- Hero -->
    <section style="min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:100px 24px {";background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460)" if template_key == "modern" else ""}">
        <div style="max-width:800px">
            <h1 style="font-size:clamp(36px,6vw,64px);font-weight:900;line-height:1.1;margin-bottom:24px">
                {config.get("hero_title", "专业落地页")}
            </h1>
            <p style="font-size:20px;color:{"#ccc" if template_key != "minimal" else "#666"};margin-bottom:40px;line-height:1.6">
                {config.get("hero_subtitle", "")}
            </p>
            <div style="display:flex;gap:16px;justify-content:center;flex-wrap:wrap">
                <a href="#features" class="btn btn-primary">了解更多</a>
                <a href="#contact" class="btn btn-outline" style="{"border:2px solid rgba(255,255,255,0.3);color:#fff" if template_key != "minimal" else "border:2px solid #333;color:#333;background:transparent"}">{config.get("cta_text", "立即联系")}</a>
            </div>
        </div>
    </section>

    <!-- Features -->
    <section class="section" style="{"background:#111" if template_key != "minimal" else "background:#f8f9fa"}">
        <div class="container">
            <h2 style="text-align:center;font-size:36px;font-weight:800;margin-bottom:48px">我们的优势</h2>
            <div class="features-grid">
                {features_html}
            </div>
        </div>
    </section>

    <!-- About -->
    <section class="section">
        <div class="container" style="max-width:800px;text-align:center">
            <h2 style="font-size:36px;font-weight:800;margin-bottom:24px">关于我们</h2>
            <p style="font-size:18px;line-height:1.8;color:{"#aaa" if template_key != "minimal" else "#666"}">{config.get("about", "")}</p>
        </div>
    </section>

    <!-- Contact -->
    <section id="contact" class="section" style="background:linear-gradient(135deg,#667eea,#764ba2);text-align:center">
        <div class="container" style="max-width:600px">
            <h2 style="font-size:36px;font-weight:800;margin-bottom:16px">联系我们</h2>
            <p style="font-size:18px;margin-bottom:40px;opacity:0.9">期待与您合作</p>
            <div style="background:rgba(255,255,255,0.1);backdrop-filter:blur(10px);border-radius:16px;padding:32px">
                {"<p style='font-size:20px;margin-bottom:12px'>📞 " + config.get("contact_phone", "") + "</p>" if config.get("contact_phone") else ""}
                {"<p style='font-size:20px'>✉️ " + config.get("contact_email", "") + "</p>" if config.get("contact_email") else ""}
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer style="padding:24px 0;text-align:center;color:#666;font-size:14px">
        <div class="container">
            <p>© 2026 {config.get("company", "")} | 由 AI建站 生成</p>
            <p style="margin-top:8px;font-size:12px;opacity:0.5">Powered by ysywlkj.xyz</p>
        </div>
    </footer>
</body>
</html>'''
    return html


@app.route("/")
def index():
    return send_from_directory("/var/www/ai-website", "index.html")


@app.route("/api/generate", methods=["POST"])
def generate():
    """生成网站 API"""
    try:
        data = request.get_json()
        description = data.get("description", "").strip()
        template = data.get("template", "modern")
        
        if not description:
            return jsonify({"ok": False, "error": "请输入业务描述"}), 400
        
        if len(description) > 500:
            return jsonify({"ok": False, "error": "描述太长，请控制在500字以内"}), 400

        print(f"[Generate] 用户输入: {description[:100]}...")
        
        # 调用 LLM
        headers = {
            "Authorization": f"Bearer {ZHIPU_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "glm-4-flash",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"请为以下业务生成落地页配置：{description}"}
            ],
            "max_tokens": 800,
            "temperature": 0.7,
        }
        
        resp = requests.post(ZHIPU_URL, headers=headers, json=payload, timeout=30)
        if resp.status_code != 200:
            print(f"[Generate] LLM error: {resp.status_code}")
            return jsonify({"ok": False, "error": "AI生成失败，请稍后重试"}), 500
        
        raw = resp.json()["choices"][0]["message"]["content"]
        
        # 解析 JSON
        config = None
        text = raw.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1])
        text = text.strip("`").strip()
        
        try:
            config = json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    config = json.loads(text[start:end])
                except:
                    pass
        
        if not config:
            return jsonify({"ok": False, "error": "AI生成格式错误，请换个描述重试"}), 500
        
        # 生成 HTML
        html = generate_html(config, template)
        
        # 保存文件
        filename = f"{uuid.uuid4().hex[:8]}.html"
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        
        url = f"{BASE_URL}/{filename}"
        print(f"[Generate] 完成: {url}")
        
        return jsonify({
            "ok": True,
            "url": url,
            "filename": filename,
            "config": {
                "title": config.get("title", ""),
                "company": config.get("company", "")
            }
        })
        
    except Exception as e:
        print(f"[Generate] Exception: {e}")
        return jsonify({"ok": False, "error": "服务器错误，请稍后重试"}), 500


@app.route("/api/templates")
def list_templates():
    """列出可用模板"""
    return jsonify({
        "ok": True,
        "templates": {k: {"name": v["name"], "desc": v["desc"]} for k, v in TEMPLATES.items()}
    })


@app.route("/api/status")
def status():
    return jsonify({"ok": True, "service": "AI建站", "version": "1.0"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
