#!/usr/bin/env python3
"""
完整流程测试: ASR → LLM → TTS
使用 demo 数据中的音频文件
"""
import asyncio
import sys
import os
from pathlib import Path

# 添加 ai_agent 到路径
sys.path.insert(0, str(Path(__file__).parent / "ai_agent"))

from core.asr_whisper import transcribe_audio
from core.llm_reasoning import generate_response
from core.tts_cosy import tts_edge


async def test_pipeline(audio_file: str, patient_name: str):
    """测试完整的语音处理流程"""
    print(f"\n{'='*60}")
    print(f"测试患者: {patient_name}")
    print(f"音频文件: {audio_file}")
    print(f"{'='*60}\n")

    # Step 1: ASR (语音转文字)
    print("📢 [1/3] 语音识别 (ASR)...")
    try:
        transcription = await transcribe_audio(audio_file)
        print(f"✅ 识别结果: {transcription}\n")
    except Exception as e:
        print(f"❌ ASR 失败: {e}")
        return

    # Step 2: LLM (生成回复)
    print("🤖 [2/3] 生成回复 (LLM)...")
    try:
        prompt = f"患者说: {transcription}\n请作为医疗助手，给出简短、友好的回复。"
        response = await generate_response(prompt)
        print(f"✅ LLM 回复: {response}\n")
    except Exception as e:
        print(f"❌ LLM 失败: {e}")
        return

    # Step 3: TTS (文字转语音)
    print("🔊 [3/3] 语音合成 (TTS)...")
    try:
        output_dir = "/tmp/test_pipeline"
        os.makedirs(output_dir, exist_ok=True)

        output_path = await tts_edge(response, output_dir)
        file_size = os.path.getsize(output_path) / 1024
        print(f"✅ 合成完成: {output_path} ({file_size:.1f} KB)\n")
    except Exception as e:
        print(f"❌ TTS 失败: {e}")
        return

    print(f"{'='*60}")
    print(f"✅ {patient_name} 完整流程测试成功!")
    print(f"{'='*60}\n")


async def main():
    """测试所有 demo 数据"""
    demo_dir = Path(__file__).parent / "ai_agent" / "data" / "demo"

    # 查找所有 .wav 文件
    audio_files = sorted(demo_dir.glob("*.wav"))

    if not audio_files:
        print("❌ 未找到音频文件")
        return

    print(f"找到 {len(audio_files)} 个音频文件")

    # 测试每个音频文件
    for audio_file in audio_files:
        patient_name = audio_file.stem  # 文件名（不含扩展名）
        await test_pipeline(str(audio_file), patient_name)

    print("\n" + "=" * 60)
    print(f"🎉 所有测试完成! 共测试 {len(audio_files)} 个样本")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
