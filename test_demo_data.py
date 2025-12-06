#!/usr/bin/env python3
"""
测试脚本:使用 ai_agent/data/demo 中的3个测试数据
自动创建用户、上传音频、查看处理结果
"""

import json
import time
import requests
from pathlib import Path

# 配置
BASE_URL = "http://localhost"
API_BASE = f"{BASE_URL}/api"
DATA_DIR = Path(__file__).parent / "ai_agent" / "data" / "demo"

# 测试数据配置
TEST_USERS = [
    {
        "json_file": "Anita.json",
        "audio_file": "Anita.wav",
        "username": "anita_test",
        "password": "test123",
    },
    {
        "json_file": "JAMES.json",
        "audio_file": "JAMES.wav",
        "username": "james_test",
        "password": "test123",
    },
    {
        "json_file": "ROSE.json",
        "audio_file": "ROSE.wav",
        "username": "rose_test",
        "password": "test123",
    },
]


def load_user_profile(json_path: Path) -> dict:
    """从JSON文件加载用户画像"""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    profile = data["metadata"]["patient_profile"]
    return {
        "name": profile["name"],
        "age": profile["age"],
        "condition": profile["condition"],
        "habits": profile["habits"],
        "common_needs": ", ".join(profile["common_needs"]),
    }


def register_user(username: str, password: str, profile: dict) -> tuple[bool, str]:
    """注册用户"""
    url = f"{API_BASE}/v1/auth/register"
    payload = {
        "username": username,
        "password": password,
        "email": f"{username}@test.com",
        **profile,
    }

    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return True, data["data"]["token"]
        else:
            # 如果已存在,尝试登录
            return login_user(username, password)
    except Exception as e:
        print(f"  ❌ 注册失败: {e}")
        return False, ""


def login_user(username: str, password: str) -> tuple[bool, str]:
    """登录用户"""
    url = f"{API_BASE}/v1/auth/login"
    payload = {"username": username, "password": password}

    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return True, data["data"]["token"]
        return False, ""
    except Exception as e:
        print(f"  ❌ 登录失败: {e}")
        return False, ""


def upload_voice(token: str, audio_path: Path) -> int:
    """上传语音文件"""
    url = f"{API_BASE}/v1/voice/upload"
    headers = {"Authorization": f"Bearer {token}"}

    with open(audio_path, "rb") as f:
        files = {"file": (audio_path.name, f, "audio/wav")}
        resp = requests.post(url, headers=headers, files=files, timeout=30)

    if resp.status_code == 200:
        data = resp.json()
        return data["data"]["record_id"]
    else:
        print(f"  ❌ 上传失败: {resp.status_code} {resp.text}")
        return 0


def check_status(token: str, record_id: int, max_wait: int = 180) -> dict:
    """轮询检查处理状态"""
    url = f"{API_BASE}/v1/voice/history"
    headers = {"Authorization": f"Bearer {token}"}

    start_time = time.time()
    last_status = ""

    while time.time() - start_time < max_wait:
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                records = data["data"]["list"]
                for rec in records:
                    if rec["ID"] == record_id:
                        status = rec["status"]

                        # 状态变化时打印
                        if status != last_status:
                            progress = {
                                "uploaded": "0%",
                                "processing_asr": "33%",
                                "processing_llm": "66%",
                                "processing_tts": "80%",
                                "done": "100%",
                                "error": "ERROR",
                            }.get(status, status)
                            print(f"    状态: {status} ({progress})")
                            last_status = status

                        # 完成或错误
                        if status in ["done", "error"]:
                            return rec

        except Exception as e:
            print(f"    查询异常: {e}")

        time.sleep(2)

    print(f"  ⏱️ 超时({max_wait}秒)")
    return {}


def print_result(result: dict):
    """打印处理结果"""
    print(f"\n  📊 最终结果:")
    print(f"    原始文本: {result.get('raw_text', 'N/A')}")
    print(f"    精炼文本: {result.get('refined_text', 'N/A')}")
    print(f"    置信度: {result.get('confidence', 0)}")
    print(f"    决策: {result.get('decision', 'N/A')}")
    print(f"    原因: {result.get('reason', 'N/A')}")
    if result.get("tts_url"):
        print(f"    TTS音频: {result['tts_url']}")


def main():
    print("=" * 60)
    print("🧪 开始测试 Demo 数据集")
    print("=" * 60)

    results = []

    for idx, user_config in enumerate(TEST_USERS, 1):
        print(f"\n[{idx}/3] 测试用户: {user_config['username']}")
        print("-" * 60)

        # 加载用户画像
        json_path = DATA_DIR / user_config["json_file"]
        audio_path = DATA_DIR / user_config["audio_file"]

        if not json_path.exists() or not audio_path.exists():
            print(f"  ❌ 文件不存在: {json_path.name} 或 {audio_path.name}")
            continue

        profile = load_user_profile(json_path)
        print(f"  👤 姓名: {profile['name']}, 年龄: {profile['age']}")

        # 注册/登录
        print(f"  🔐 注册/登录...")
        success, token = register_user(
            user_config["username"], user_config["password"], profile
        )

        if not success:
            print(f"  ❌ 认证失败,跳过")
            continue

        print(f"  ✅ 认证成功")

        # 上传音频
        print(f"  📤 上传音频: {audio_path.name}")
        record_id = upload_voice(token, audio_path)

        if not record_id:
            print(f"  ❌ 上传失败,跳过")
            continue

        print(f"  ✅ 上传成功,记录ID: {record_id}")

        # 等待处理
        print(f"  ⏳ 等待AI处理...")
        result = check_status(token, record_id, max_wait=180)

        if result:
            print_result(result)
            results.append(
                {
                    "username": user_config["username"],
                    "record_id": record_id,
                    "status": result.get("status"),
                    "decision": result.get("decision"),
                    "success": result.get("status") == "done",
                }
            )
        else:
            print(f"  ❌ 处理超时")
            results.append(
                {
                    "username": user_config["username"],
                    "record_id": record_id,
                    "success": False,
                }
            )

    # 总结
    print("\n" + "=" * 60)
    print("📋 测试总结")
    print("=" * 60)

    success_count = sum(1 for r in results if r.get("success"))
    print(f"总计: {len(results)}/{len(TEST_USERS)}")
    print(f"成功: {success_count}")
    print(f"失败: {len(results) - success_count}")

    print("\n详细结果:")
    for r in results:
        status_icon = "✅" if r.get("success") else "❌"
        print(
            f"  {status_icon} {r['username']} (ID={r['record_id']}) - {r.get('status', 'unknown')}"
        )


if __name__ == "__main__":
    # 检查服务是否运行
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/user/profile", timeout=3)
    except:
        print("❌ 错误: 服务未启动!")
        print("请先运行: docker compose up -d")
        exit(1)

    main()
