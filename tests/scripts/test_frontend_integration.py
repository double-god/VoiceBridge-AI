"""
前端集成测试: 模拟前端上传音频 -> 后端处理 -> AI 处理
"""

import requests
import time
import json

# 配置
BACKEND_URL = "http://localhost:80/api/v1"  # Nginx 转发后的地址
TEST_AUDIO = "./ai_agent/data/demo/Anita.wav"  # 测试音频文件


def test_frontend_flow():
    """测试完整的前端流程"""

    print("=" * 60)
    print("🧪 前端集成测试: 上传 -> 处理 -> 结果")
    print("=" * 60)

    # Step 1: 用户登录 (获取 token)
    print("\n📝 Step 1: 用户登录...")
    login_response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={"username": "test_user", "password": "test123"},
    )

    if login_response.status_code == 200:
        token = login_response.json().get("data", {}).get("token")
        print(f"✅ 登录成功, Token: {token[:20]}...")
    else:
        print("❌ 登录失败, 尝试注册...")
        # 注册新用户
        register_response = requests.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "username": "test_user",
                "password": "test123",
                "email": "test@example.com",
            },
        )
        if register_response.status_code == 200:
            token = register_response.json().get("data", {}).get("token")
            print(f"✅ 注册成功, Token: {token[:20]}...")
        else:
            print(f"❌ 注册失败: {register_response.text}")
            return

    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: 上传音频
    print("\n📤 Step 2: 上传音频文件...")
    with open(TEST_AUDIO, "rb") as f:
        files = {"file": ("recording.wav", f, "audio/wav")}
        upload_response = requests.post(
            f"{BACKEND_URL}/voice/upload", files=files, headers=headers
        )

    if upload_response.status_code != 200:
        print(f"❌ 上传失败: {upload_response.text}")
        return

    upload_data = upload_response.json().get("data", {})
    record_id = upload_data.get("record_id")
    print(f"✅ 上传成功, Record ID: {record_id}")

    # Step 3: SSE 监听处理进度
    print("\n⏳ Step 3: 监听处理进度 (SSE)...")
    print("─" * 60)

    sse_url = f"{BACKEND_URL}/voice/progress/{record_id}"

    try:
        response = requests.get(sse_url, headers=headers, stream=True, timeout=120)

        for line in response.iter_lines():
            if line:
                line_str = line.decode("utf-8")

                # 解析 SSE 数据
                if line_str.startswith("data: "):
                    data_str = line_str[6:]  # 去掉 "data: " 前缀

                    try:
                        event_data = json.loads(data_str)
                        status = event_data.get("status")

                        # 打印进度
                        if status == "processing_asr":
                            print("🎤 正在进行语音识别...")
                        elif status == "processing_llm":
                            raw_text = event_data.get("raw_text", "")
                            print(f"📝 ASR 完成: {raw_text[:50]}...")
                            print("🧠 正在进行意图理解...")
                        elif status == "processing_tts":
                            refined_text = event_data.get("refined_text", "")
                            confidence = event_data.get("confidence", 0)
                            decision = event_data.get("decision", "unknown")
                            print(f"💡 LLM 完成:")
                            print(f"   决策: {decision}")
                            print(f"   置信度: {confidence}")
                            print(f"   精炼文本: {refined_text[:50]}...")
                            print("🔊 正在合成语音...")
                        elif status == "completed":
                            tts_url = event_data.get("tts_url", "")
                            print(f"✅ 全部完成!")
                            print(f"   TTS URL: {tts_url}")
                            break
                        elif status == "error":
                            reason = event_data.get("reason", "Unknown error")
                            print(f"❌ 处理失败: {reason}")
                            break

                    except json.JSONDecodeError:
                        pass

    except requests.exceptions.Timeout:
        print("⏱️ 超时: 处理时间超过 120 秒")
    except Exception as e:
        print(f"❌ 错误: {e}")

    print("\n" + "=" * 60)
    print("🎉 测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    test_frontend_flow()
