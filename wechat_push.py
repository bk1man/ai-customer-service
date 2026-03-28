"""
微信主动发消息工具
"""

import requests
import time

# 微信公众号凭证
APPID = "wx4bf0c5fd794ea6c6"
APPSECRET = "01fc695af6ecc5c47b021c7a59ba9168"

_cached_token = None
_token_expires_at = 0

def get_access_token() -> str:
    """获取微信access_token，带缓存"""
    global _cached_token, _token_expires_at
    if _cached_token and time.time() < _token_expires_at:
        return _cached_token
    
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if "access_token" in data:
            _cached_token = data["access_token"]
            _token_expires_at = time.time() + int(data.get("expires_in", 7200)) - 300
            return _cached_token
        else:
            print(f"[WeChat] get_token error: {data}")
    except Exception as e:
        print(f"[WeChat] get_token exception: {e}")
    return None
