"""
完整流程测试: ASR → LLM → TTS
测试使用 demo 数据中的 Anita 案例
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, "/app")

from core.asr_whisper import transcribe
from core.llm_reasoning import infer_intent
from core.tts_cosy import tts_edge


async def test_full_pipeline(sample_name="Anita"):
    """
    测试完整的语音处理流程

    Args:
        sample_name: 测试样本名称 (Anita, JAMES, ROSE)
    """
    print("=" * 60)
    print("🧪 完整流程测试: ASR → LLM → TTS")
    print("=" * 60)

    # 数据路径
    json_file = f"/app/data/demo/{sample_name}.json"
    audio_path = f"/app/data/demo/{sample_name}.wav"

    # 检查文件
    if not os.path.exists(json_file):
        print(f"❌ 配置文件不存在: {json_file}")
        return
    if not os.path.exists(audio_path):
        print(f"❌ 音频文件不存在: {audio_path}")
        return

    # 读取用户档案
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    profile = data["metadata"]["patient_profile"]

    print(f"\n📁 测试数据: {sample_name}")
    print(f'👤 用户: {profile["name"]}, {profile["age"]}岁')
    print(f'📝 状况: {profile["condition"]}')
    print(f"🎵 音频: {audio_path}")

    # ============================================================
    # Step 1: ASR (语音识别)
    # ============================================================
    print("\n" + "─" * 60)
    print("📝 Step 1: 语音识别 (ASR)")
    print("─" * 60)

    transcription = transcribe(audio_path)
    print(f"✅ 识别结果 ({len(transcription)} 字符):")
    print(f"   {transcription[:200]}...")

    # ============================================================
    # Step 2: LLM (意图理解)
    # ============================================================
    print("\n" + "─" * 60)
    print("🧠 Step 2: 意图理解 (LLM)")
    print("─" * 60)

    user_profile = {
        "name": profile["name"],
        "age": profile["age"],
        "condition": profile["condition"],
        "habits": profile.get("habits", ""),
        "common_needs": profile.get("common_needs", []),
    }

    intent_result = infer_intent(transcription, user_profile)

    print(f"✅ 意图分析:")
    print(f'   决策: {intent_result["decision"]}')
    print(f'   置信度: {intent_result["confidence"]}')
    print(f'   原因: {intent_result["reason"][:100]}...')
    print(f'   精炼文本: {intent_result["refined_text"][:150]}...')

    # ============================================================
    # Step 3: TTS (语音合成)
    # ============================================================
    print("\n" + "─" * 60)
    print("🔊 Step 3: 语音合成 (TTS)")
    print("─" * 60)

    # 使用精炼后的文本前80字作为响应
    response_text = intent_result["refined_text"][:80] + "..."
    print(f"📢 待合成文本: {response_text}")

    # 保存到 output 目录（挂载到宿主机）
    output_dir = "/app/output"
    os.makedirs(output_dir, exist_ok=True)

    output_path = await tts_edge(response_text, output_dir)
    file_size = os.path.getsize(output_path) / 1024

    # 转换为相对路径显示
    relative_path = output_path.replace("/app/", "")
    print(f"✅ 语音合成完成: {relative_path} ({file_size:.1f} KB)")

    # ============================================================
    # 测试总结
    # ============================================================
    print("\n" + "=" * 60)
    print("🎉 完整流程测试成功！")
    print("   ASR: Whisper (base) ✓")
    print("   LLM: DashScope qwen-max ✓")
    print("   TTS: CosyVoice-300M-SFT ✓")
    print("=" * 60)
    print(f"\n💾 生成的语音文件: {output_path}")


if __name__ == "__main__":
    # 支持命令行参数指定测试样本
    sample = sys.argv[1] if len(sys.argv) > 1 else "Anita"
    asyncio.run(test_full_pipeline(sample))
