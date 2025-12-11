#!/usr/bin/env python3
"""
快速测试脚本 - 只测试一个文件，用于验证系统是否工作
"""
import requests
import time
import sys

API_BASE = "http://localhost"
TEST_FILE = "ai_agent/data/demo/anita_test/Anita.wav"


def quick_test():
    """快速测试一个音频文件"""

    print("\n" + "=" * 60)
    print("🚀 VoiceBridge AI - 快速测试")
    print("=" * 60 + "\n")

    # 1. 登录
    print("1️⃣ 正在登录...")
    try:
        resp = requests.post(
            f"{API_BASE}/api/user/login",
            json={"username": "nainong", "password": "11111111"},
            timeout=10,
        )
        resp.raise_for_status()
        token = resp.json()["data"]["token"]
        print("   ✅ 登录成功\n")
    except Exception as e:
        print(f"   ❌ 登录失败: {e}\n")
        return False

    headers = {"Authorization": f"Bearer {token}"}

    # 2. 上传文件
    print("2️⃣ 正在上传音频...")
    try:
        with open(TEST_FILE, "rb") as f:
            files = {"audio": ("test.wav", f, "audio/wav")}
            resp = requests.post(
                f"{API_BASE}/api/voice/upload", files=files, headers=headers, timeout=30
            )
        resp.raise_for_status()
        record_id = resp.json()["data"]["id"]
        print(f"   ✅ 上传成功 (ID: {record_id})\n")
    except Exception as e:
        print(f"   ❌ 上传失败: {e}\n")
        return False

    # 3. 等待处理（最多 3 分钟）
    print("3️⃣ 等待处理完成...")
    for i in range(36):  # 36 * 5 = 180秒
        try:
            resp = requests.get(
                f"{API_BASE}/api/voice/record/{record_id}", headers=headers, timeout=10
            )
            resp.raise_for_status()
            data = resp.json()["data"]
            status = data["status"]

            if status == "completed":
                print(f"\n   ✅ 处理完成！\n")
                print(f"   📝 ASR 结果: {data.get('asr_text', 'N/A')[:100]}...")
                print(f"   🤖 LLM 结果: {data.get('llm_text', 'N/A')[:100]}...")
                return True
            elif status in ["error", "agent_failed", "cancelled"]:
                print(f"\n   ❌ 处理失败: {status}\n")
                return False
            else:
                print(f"   ⏳ {status}... ({i*5}秒)")
                time.sleep(5)
        except Exception as e:
            print(f"   ⚠️ 查询出错: {e}")
            time.sleep(5)

    print(f"\n   ⏱️ 超时（180秒）\n")
    return False


if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1)
