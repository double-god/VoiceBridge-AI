#!/usr/bin/env python3
"""
容器内 TTS 测试脚本
"""
import asyncio
import os
from core import tts_cosy


async def test_tts():
    """测试 CosyVoice TTS"""
    print("=" * 60)
    print("CosyVoice TTS 测试")
    print("=" * 60)

    test_texts = [
        "Hello, this is a test of the text to speech system.",
        "The patient is doing well and shows good progress.",
        "你好，这是一个语音合成测试。",
    ]

    output_dir = "/tmp/tts_test"
    os.makedirs(output_dir, exist_ok=True)

    for i, text in enumerate(test_texts, 1):
        print(f"\n[{i}/{len(test_texts)}] 测试文本: {text}")
        try:
            output_path = await tts_cosy.tts_edge(text, output_dir)

            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"✅ 成功!")
                print(f"   文件: {output_path}")
                print(f"   大小: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            else:
                print(f"❌ 失败: 文件未生成")

        except Exception as e:
            print(f"❌ 异常: {e}")
            import traceback

            traceback.print_exc()

    print("\n" + "=" * 60)
    print("测试完成!")
    print(f"输出目录: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_tts())
