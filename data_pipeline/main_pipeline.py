#!/usr/bin/env python3
"""
数据处理流水线入口
一键执行：转码 -> 解析 -> 生成 JSON -> 复制到 ai_agent

Usage:
    python main_pipeline.py
"""

import shutil
from pathlib import Path

from processors import batch_convert
from parsers import ChaParser
from loaders import DemoLoader


# 路径配置
BASE_DIR = Path(__file__).parent
ASSETS_VIDEO_DIR = BASE_DIR / "assets" / "video"
ASSETS_CHA_DIR = BASE_DIR / "assets" / "cha"
OUTPUT_DIR = BASE_DIR / "output" / "demo"
AGENT_DATA_DIR = BASE_DIR.parent / "ai_agent" / "data" / "demo"


def step1_convert_videos():
    """步骤1: 转换视频为音频"""
    print("\n" + "=" * 50)
    print("📹 步骤 1: 转换 MP4 -> WAV")
    print("=" * 50)

    wav_dir = OUTPUT_DIR / "wav"
    wav_files = batch_convert(ASSETS_VIDEO_DIR, wav_dir)

    print(f"转换完成: {len(wav_files)} 个文件")
    return wav_files


def step2_parse_cha_files():
    """步骤2: 解析 .cha 转写文件"""
    print("\n" + "=" * 50)
    print("📝 步骤 2: 解析 .cha 文件")
    print("=" * 50)

    parser = ChaParser()
    cha_files = list(ASSETS_CHA_DIR.glob("*.cha"))

    if not cha_files:
        print("⚠️ 未找到 .cha 文件，跳过此步骤")
        print("💡 提示: 如果没有 .cha 文件，可以手动创建 JSON 或使用 ASR 生成")
        return {}

    results = {}
    for cha_file in cha_files:
        try:
            doc = parser.parse(cha_file)
            results[cha_file.stem] = parser.to_dict(doc)
            print(f"✅ 解析成功: {cha_file.name} ({len(doc.utterances)} 条话语)")
        except Exception as e:
            print(f"❌ 解析失败 {cha_file.name}: {e}")

    return results


def step3_generate_samples(wav_files: list[Path], cha_data: dict):
    """步骤3: 生成样本 JSON 文件"""
    print("\n" + "=" * 50)
    print("📦 步骤 3: 生成样本 JSON")
    print("=" * 50)

    samples_dir = OUTPUT_DIR / "samples"
    samples_dir.mkdir(parents=True, exist_ok=True)

    for wav_file in wav_files:
        sample_id = wav_file.stem

        # 复制 WAV 到 samples 目录
        target_wav = samples_dir / wav_file.name
        shutil.copy(wav_file, target_wav)

        # 生成对应的 JSON
        json_path = samples_dir / f"{sample_id}.json"

        # 尝试匹配 .cha 数据
        utterances = []
        metadata = {"source": "demo"}

        if sample_id in cha_data:
            utterances = cha_data[sample_id].get("utterances", [])
            metadata.update(cha_data[sample_id].get("metadata", {}))
            metadata["has_cha"] = True
        else:
            # 没有 .cha 文件，创建空的占位 JSON
            # 后续可以用 ASR 填充
            metadata["has_cha"] = False
            print(f"⚠️ {sample_id}: 无匹配的 .cha 文件，创建空 JSON")
        
        DemoLoader.create_sample_json(
            output_path=json_path,
            sample_id=sample_id,
            utterances=utterances,
            metadata=metadata
        )
    
    print(f"✅ 生成完成: {len(wav_files)} 个样本")
    return samples_dir


def step4_copy_to_agent(samples_dir: Path):
    """步骤4: 复制到 ai_agent/data/"""
    print("\n" + "=" * 50)
    print("📤 步骤 4: 复制到 ai_agent/data/")
    print("=" * 50)
    
    # 清空目标目录
    if AGENT_DATA_DIR.exists():
        shutil.rmtree(AGENT_DATA_DIR)
    
    # 复制
    shutil.copytree(samples_dir, AGENT_DATA_DIR)
    
    print(f"✅ 数据已同步到: {AGENT_DATA_DIR}")


def step5_verify():
    """步骤5: 验证数据"""
    print("\n" + "=" * 50)
    print("🔍 步骤 5: 验证数据")
    print("=" * 50)
    
    loader = DemoLoader(AGENT_DATA_DIR)
    
    print(f"样本总数: {len(loader)}")
    print("\n样本列表:")
    for sample in loader:
        has_transcript = "✅" if sample.transcript else "⚠️ 无转写"
        print(f"  - {sample.sample_id}: {sample.audio_path.name} {has_transcript}")


def main():
    """主流程"""
    print("🚀 VoiceBridge 数据处理流水线")
    print("=" * 50)
    
    # 确保输出目录存在
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 执行各步骤
    wav_files = step1_convert_videos()
    
    if not wav_files:
        print("\n❌ 没有找到视频文件，请将 MP4 文件放入:")
        print(f"   {ASSETS_VIDEO_DIR}")
        return
    
    cha_data = step2_parse_cha_files()
    samples_dir = step3_generate_samples(wav_files, cha_data)
    step4_copy_to_agent(samples_dir)
    step5_verify()
    
    print("\n" + "=" * 50)
    print("🎉 数据处理完成!")
    print("=" * 50)
    print(f"\n下一步: 运行 ai_agent 服务测试数据加载")
    print(f"  cd ../ai_agent && python main.py")


if __name__ == "__main__":
    main()
