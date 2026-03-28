"""
微信公众号AI客服 - Flask主应用
AI Customer Service for WeChat Public Account
"""

from flask import Flask, request, make_response
import hashlib
from wechat_handler import WeChatHandler
from knowledge_base import KnowledgeBase

app = Flask(__name__)

# 微信公众号配置
WECHAT_TOKEN = "your_token_here"  # 需要在微信公众号后台配置
WECHAT_APPID = "wx4bf0c5fd794ea6c6"
WECHAT_APPSECRET = "01fc695af6ecc5c47b021c7a59ba9168"

# 初始化组件
knowledge_base = KnowledgeBase()
wechat_handler = WeChatHandler(knowledge_base)


@app.route("/")
def index():
    """首页"""
    return "WeChat AI Customer Service is running!"


@app.route("/wechat", methods=["GET", "POST"])
def wechat():
    """
    微信公众号服务器配置URL验证（GET）
    接收用户消息（POST）
    """
    if request.method == "GET":
        # 验证微信服务器签名
        signature = request.args.get("signature", "")
        timestamp = request.args.get("timestamp", "")
        nonce = request.args.get("nonce", "")
        echostr = request.args.get("echostr", "")

        # 验证签名
        tmp_list = sorted([WECHAT_TOKEN, timestamp, nonce])
        tmp_str = "".join(tmp_list)
        hash_str = hashlib.sha1(tmp_str.encode("utf-8")).hexdigest()

        if hash_str == signature:
            return make_response(echostr)
        else:
            return "验证失败", 400
    else:
        # 处理用户发送的消息
        xml_data = request.data
        response = wechat_handler.process_message(xml_data)
        return make_response(response)


@app.route("/api/knowledge/add", methods=["POST"])
def add_knowledge():
    """添加知识库条目（管理接口）"""
    data = request.get_json()
    question = data.get("question", "")
    answer = data.get("answer", "")
    keywords = data.get("keywords", [])

    if question and answer:
        knowledge_base.add_qa(question, answer, keywords)
        return {"success": True, "message": "知识添加成功"}
    return {"success": False, "message": "参数不完整"}


@app.route("/api/knowledge/list", methods=["GET"])
def list_knowledge():
    """获取知识库列表"""
    items = knowledge_base.list_all()
    return {"success": True, "data": items}


@app.route("/api/status", methods=["GET"])
def status():
    """服务状态检查"""
    return {
        "status": "running",
        "knowledge_count": knowledge_base.count(),
        "version": "1.0.0"
    }


if __name__ == "__main__":
    print("=" * 50)
    print("微信公众号AI客服演示系统")
    print("=" * 50)
    print(f"服务地址: http://0.0.0.0:5000")
    print(f"微信回调: http://0.0.0.0:5000/wechat")
    print("=" * 50)

    # 本地开发模式
    app.run(host="0.0.0.0", port=5000, debug=True)
