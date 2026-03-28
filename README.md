# 微信公众号AI客服演示

一个简单的微信公众号AI客服演示项目，基于Flask实现，支持关键词匹配自动回复和LLM接入预留。

## 功能特性

- ✅ 微信公众号消息回调接入
- ✅ 关键词匹配自动回复
- ✅ 简单知识库管理
- ✅ LLM接入预留接口
- ✅ 管理API接口

## 目录结构

```
ai-customer-service/
├── app.py              # Flask主应用
├── wechat_handler.py   # 微信消息处理
├── knowledge_base.py   # 知识库模块
├── requirements.txt    # Python依赖
└── README.md           # 说明文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置微信公众号

在微信公众号后台配置服务器地址：
- URL: `https://your-domain.com/wechat`
- Token: 与app.py中的WECHAT_TOKEN保持一致
- 消息加密方式: 明文模式（或根据需要配置）

### 3. 修改配置

编辑 `app.py`，修改以下配置：

```python
WECHAT_TOKEN = "your_custom_token"  # 设置自定义Token
WECHAT_APPID = "your_appid"         # 你的AppID
WECHAT_APPSECRET = "your_appsecret" # 你的AppSecret
```

### 4. 启动服务

```bash
python app.py
```

服务将在 `http://0.0.0.0:5000` 启动。

## API接口

### 知识库管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/knowledge/add` | POST | 添加知识库条目 |
| `/api/knowledge/list` | GET | 获取知识库列表 |
| `/api/status` | GET | 服务状态检查 |

### 添加知识示例

```bash
curl -X POST http://localhost:5000/api/knowledge/add \
  -H "Content-Type: application/json" \
  -d '{"question":"问题","answer":"回答","keywords":["关键词1","关键词2"]}'
```

## 接入LLM（如GPT）

在 `wechat_handler.py` 的 `handle_text` 方法中，取消注释LLM调用代码：

```python
# TODO: 接入LLM API
answer = await self.call_llm(content)
```

伪代码示例：

```python
def call_llm(user_message: str) -> str:
    """
    调用大语言模型接口
    """
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": user_message}]
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json=payload
    )
    return response.json()["choices"][0]["message"]["content"]
```

## 部署建议

### 生产环境

1. 使用Gunicorn或uWSGI替代开发服务器
2. 配置HTTPS（微信要求）
3. 使用nginx反向代理
4. 配置防火墙和CORS

### Docker部署示例

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

## 默认知识库

系统预置了常见问答：
- 工作时间
- 联系方式
- 产品价格
- 产品介绍
- 使用方法
- 退款政策

## 注意事项

1. 微信公众号后台需要配置服务器URL才能接收消息
2. 生产环境务必使用HTTPS
3. 建议定期备份知识库数据
4. LLM接入需要自行申请API Key

## License

MIT License
