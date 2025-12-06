#!/usr/bin/env python3
"""
测试 TTS 功能

这个脚本会:
1. 测试直接调用 CosyVoice TTS 服务
2. 触发完整的 pipeline (包含 TTS)
"""
import asyncio
import os
import sys

# 添加 ai_agent 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "ai_agent"))


async def test_direct_tts():
    """测试直接调用 TTS"""
    print("\n=== 测试 1: 直接调用 CosyVoice TTS ===")

    from core import tts_cosy

    test_texts = [
        "Hello, this is a test of the text to speech system.",
        "你好，这是一个语音合成测试。",
    ]

    output_dir = "/tmp/tts_test"
    os.makedirs(output_dir, exist_ok=True)

    for i, text in enumerate(test_texts, 1):
        print(f"\n测试 {i}: {text}")
        try:
            output_path = await tts_cosy.tts_edge(text, output_dir)

            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"✅ TTS 成功!")
                print(f"   输出文件: {output_path}")
                print(f"   文件大小: {file_size} bytes")
            else:
                print(f"❌ 失败: 文件未生成")

        except Exception as e:
            print(f"❌ 异常: {e}")
            import traceback

            traceback.print_exc()


async def test_pipeline_with_tts():
    """测试完整 pipeline (需要触发 accept decision)"""
    print("\n=== 测试 2: 完整 Pipeline (ASR → LLM → TTS) ===")
    print("注意: 只有当 LLM decision='accept' 时才会触发 TTS\n")

    # 使用一个可能触发 accept 的音频文件
    demo_files = [
        "ai_agent/data/demo/Anita.wav",
        "ai_agent/data/demo/JAMES.wav",
        "ai_agent/data/demo/ROSE.wav",
    ]

    from services.pipeline import process_voice_record
    from core.database import get_db_session

    # 检查哪些文件存在
    available_files = [f for f in demo_files if os.path.exists(f)]

    if not available_files:
        print("❌ 没有找到演示音频文件")
        return

    print(f"找到 {len(available_files)} 个演示文件")

    # 只测试第一个文件
    test_file = available_files[0]
    print(f"\n使用文件: {test_file}")

    # 模拟上传到 MinIO 并处理
    # 注意: 这需要 MinIO 和数据库都在运行
    print("\n提示: 要完整测试 pipeline, 需要:")
    print("1. MinIO 服务运行中")
    print("2. PostgreSQL 数据库运行中")
    print("3. 通过 API 接口 POST /api/v1/voice/process")
    print("\n推荐使用 curl 或前端上传真实音频文件来测试完整流程")


async def main():
    print("=" * 60)
    print("CosyVoice TTS 测试")
    print("=" * 60)

    # 测试直接 TTS 调用
    await test_direct_tts()

    # 提示如何测试完整 pipeline
    await test_pipeline_with_tts()

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
