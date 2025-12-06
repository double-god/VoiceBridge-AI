#!/usr/bin/env python3
"""简单测试单个Demo数据"""
import requests
import json
from pathlib import Path

DATA_DIR = Path("ai_agent/data/demo")

# 加载Anita数据
with open(DATA_DIR / "Anita.json") as f:
    data = json.load(f)
    profile = data["metadata"]["patient_profile"]

# 注册
print("1. 注册用户...")
resp = requests.post(
    "http://localhost/api/v1/auth/register",
    json={
        "username": "anita_demo",
        "password": "test123",
        "email": "anita@test.com",
        "name": profile["name"],
        "age": profile["age"],
        "condition": profile["condition"],
        "habits": profile["habits"],
        "common_needs": ", ".join(profile["common_needs"]),
    },
)
print(f"状态: {resp.status_code}")
if resp.status_code != 200:
    print(f"失败: {resp.text}")
    # 尝试登录
    print("\n尝试登录...")
    resp = requests.post(
        "http://localhost/api/v1/auth/login",
        json={"username": "anita_demo", "password": "test123"},
    )

token = resp.json()["data"]["token"]
print(f"Token: {token[:50]}...")

# 上传音频
print("\n2. 上传音频...")
with open(DATA_DIR / "Anita.wav", "rb") as f:
    files = {"file": ("Anita.wav", f, "audio/wav")}
    resp = requests.post(
        "http://localhost/api/v1/voice/upload",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )

print(f"状态: {resp.status_code}")
data = resp.json()
print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")

if resp.status_code == 200:
    record_id = data["data"]["record_id"]
    print(f"\n✅ 上传成功! Record ID: {record_id}")
    print("\n查看处理进度:")
    print(f"http://localhost/api/v1/voice/history (使用 Bearer token)")
    print(f"\n监控日志: docker compose logs -f ai_agent")
