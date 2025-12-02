"""
Demo 数据集加载脚本
将视频转码、清洗并生成 JSON 数据集
"""

import json
import sys
from pathlib import Path

# 把根目录加到路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from data_pipeline.loaders.demo_loader import DemoLoader  # noqa: E402
from data_pipeline.processors.audio_cleaner import batch_clean_audio  # noqa: E402


# 路径配置
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
VIDEO_DIR = PROJECT_ROOT / "data_pipeline" / "assets" / "video"  # 视频源目录
DATA_DIR = BASE_DIR / "data" / "demo"  # JSON + WAV 输出目录
OUTPUT_JSON_PATH = BASE_DIR / "data" / "grand_round_dataset.json"


def samples_to_dict(samples: list) -> list[dict]:
    """将 Sample 对象列表转为可序列化的字典列表"""
    return [
        {
            "sample_id": s.sample_id,
            "audio_path": str(s.audio_path),
            "transcript": s.transcript,
            "metadata": s.metadata,
        }
        for s in samples
    ]


def main():
    print("[开始] 执行数据集演示加载...")

    # 确保目录存在
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 初始化加载器
    # data_dir: JSON 配置文件 + 输出 WAV 的目录
    # video_dir: 原始视频目录
    loader = DemoLoader(data_dir=DATA_DIR, video_dir=VIDEO_DIR)

    # 加载数据 (自动转码)
    samples = loader.load()
    print(f"[完成] 转码了 {len(samples)} 个样本")

    if not samples:
        print("[警告] 无样本可导出")
        return

    # 音频清洗：降噪 + 静音切分 + 归一化 + 重采样到 16kHz
    print("[开始] 音频清洗...")
    batch_clean_audio(
        DATA_DIR,
        pattern="*.wav",
        sample_rate=16000,  # Whisper 推荐
        normalize=True,
        denoise=True,
        remove_silence=True,
    )

    # 转换并保存为 JSON
    OUTPUT_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = samples_to_dict(samples)

    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"[完成] 数据集已保存到 {OUTPUT_JSON_PATH}")


if __name__ == "__main__":
    main()
