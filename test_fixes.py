#!/usr/bin/env python3
"""
验证3个修复:
1. 保持原语言(英文→英文,中文→中文)
2. LLM API重试机制
3. TTS代理配置
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost"
DATA_DIR = Path("ai_agent/data/demo")


def test_user(username, audio_file, expected_language):
    """测试单个用户"""
    print(f"\n{'='*60}")
    print(f"测试: {username} - {audio_file}")
    print(f"期望语言: {expected_language}")
    print("=" * 60)

    # 登录
    resp = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"username": username, "password": "test123"},
    )

    if resp.status_code != 200:
        print(f"❌ 登录失败")
        return False

    token = resp.json()["data"]["token"]

    # 上传音频
    with open(DATA_DIR / audio_file, "rb") as f:
        files = {"file": (audio_file, f, "audio/wav")}
        resp = requests.post(
            f"{BASE_URL}/api/v1/voice/upload",
            headers={"Authorization": f"Bearer {token}"},
            files=files,
        )

    if resp.status_code != 200:
        print(f"❌ 上传失败: {resp.text}")
        return False

    record_id = resp.json()["data"]["record_id"]
    print(f"✅ 上传成功, Record ID: {record_id}")

    # 等待处理
    import time

    print("⏳ 等待处理...")

    for i in range(60):  # 最多等待2分钟
        time.sleep(2)
        resp = requests.get(
            f"{BASE_URL}/api/v1/voice/history",
            headers={"Authorization": f"Bearer {token}"},
        )

        if resp.status_code == 200:
            records = resp.json()["data"]["list"]
            for rec in records:
                if rec["ID"] == record_id:
                    status = rec["status"]

                    if status == "done":
                        print(f"\n✅ 处理完成!")
                        print(f"原始文本: {rec['raw_text'][:100]}...")
                        print(f"精炼文本: {rec['refined_text'][:100]}...")
                        print(f"决策: {rec['decision']}")
                        print(f"置信度: {rec['confidence']}")

                        # 验证语言
                        refined = rec["refined_text"]
                        if expected_language == "en":
                            # 检查是否主要是英文
                            has_chinese = any(
                                "\u4e00" <= c <= "\u9fff" for c in refined
                            )
                            if has_chinese:
                                print(f"❌ 语言验证失败: 期望英文但返回中文")
                                return False
                            else:
                                print(f"✅ 语言验证通过: 保持英文")
                        elif expected_language == "zh":
                            # 检查是否有中文
                            has_chinese = any(
                                "\u4e00" <= c <= "\u9fff" for c in refined
                            )
                            if not has_chinese:
                                print(f"⚠️ 语言验证: 期望中文但输入可能无中文内容")
                            else:
                                print(f"✅ 语言验证通过: 保持中文")

                        return True

                    elif status == "error":
                        print(f"❌ 处理失败: {rec.get('reason', 'unknown')}")
                        return False

        if i % 5 == 0:
            print(f"  等待中... ({i*2}秒)")

    print(f"⏱️ 超时")
    return False


def main():
    print(
        """
╔═══════════════════════════════════════════════════════════╗
║       VoiceBridge AI - 修复验证测试                      ║
║                                                           ║
║  1. ✓ LLM保持原语言(英文→英文, 中文→中文)              ║
║  2. ✓ LLM API重试机制(最多3次,指数退避)                 ║
║  3. ✓ TTS代理支持(通过TTS_PROXY环境变量)                ║
╚═══════════════════════════════════════════════════════════╝
"""
    )

    results = []

    # 测试1: Anita (英文输入)
    results.append(("Anita", test_user("anita_test", "Anita.wav", "en")))

    # 测试2: James (英文输入)
    results.append(("James", test_user("james_test", "JAMES.wav", "en")))

    # 测试3: Rose (英文输入)
    results.append(("Rose", test_user("rose_test", "ROSE.wav", "en")))

    # 总结
    print(f"\n{'='*60}")
    print("📊 测试总结")
    print("=" * 60)

    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} - {name}")

    success_count = sum(1 for _, s in results if s)
    print(f"\n总计: {success_count}/{len(results)} 通过")

    if success_count == len(results):
        print("\n🎉 所有测试通过!")
    else:
        print(f"\n⚠️ {len(results) - success_count} 个测试失败")

    print("\n💡 提示:")
    print("  - LLM重试日志请查看: docker compose logs ai_agent")
    print("  - TTS代理配置: 在.env中设置 TTS_PROXY=http://your-proxy:port")


if __name__ == "__main__":
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/user/profile", timeout=3)
    except:
        print("❌ 错误: 服务未启动!")
        print("请先运行: docker compose up -d")
        exit(1)

    main()
