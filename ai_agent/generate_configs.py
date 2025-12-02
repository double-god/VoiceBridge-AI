"""
批量生成视频配置 JSON
用法: python generate_configs.py
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
VIDEO_DIR = PROJECT_ROOT / "data_pipeline" / "assets" / "video"  # 视频源目录
CONFIG_DIR = BASE_DIR / "data" / "demo"  # 配置输出目录

# 患者画像元数据 (对应 FRD 中的 F5 患者画像配置)
CASE_STUDY_METADATA = {
    "Anita": {
        "description": "Case Study 1: Cognitively Unimpaired",
        "patient_profile": {
            "name": "Anita",
            "age": 77,
            "condition": "Diabetes, Hypertension, Memory difficulties (forgetting names/intentions)",
            "habits": "Yoga, Pickleball, Writing memoir, Book club",
            "common_needs": [
                "Remind me why I came here",
                "What is that person's name?",
            ],
        },
    },
    "JAMES": {
        "description": "Case Study 2: Mild Neurocognitive Disorder (NCD)",
        "patient_profile": {
            "name": "James",
            "age": 76,
            "condition": "Mild NCD, Bilateral mild hearing loss, High cholesterol",
            "habits": "Nightly walks, Board games, Eating fast food",
            "common_needs": [
                "Find my wallet",
                "Set alarm for appointment",
                "Check phone",
            ],
        },
    },
    "ROSE": {
        "description": "Case Study 3: Major Neurocognitive Disorder",
        "patient_profile": {
            "name": "Rose",
            "age": 83,
            "condition": "Major NCD, Hearing loss (lost hearing aids), Hypertension",
            "habits": "Spending time with dogs, Visiting family",
            "common_needs": [
                "Find hearing aids",
                "Brush teeth reminder",
                "Help with self-care",
            ],
        },
    },
}


def get_metadata(sample_id: str) -> dict:
    """获取样本的元数据，优先使用预定义的患者画像"""
    if sample_id in CASE_STUDY_METADATA:
        return CASE_STUDY_METADATA[sample_id]
    # 未知样本使用默认元数据
    return {
        "description": f"视频: {sample_id}.mp4",
        "source": "local",
    }


def main():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    video_files = list(VIDEO_DIR.glob("*.mp4"))

    if not video_files:
        print(f"[警告] 未找到视频文件: {VIDEO_DIR}")
        print("[提示] 请将 .mp4 文件放入 assets/video/ 目录")
        return

    created = 0
    for video_path in video_files:
        sample_id = video_path.stem  # 文件名去掉扩展名
        config_path = CONFIG_DIR / f"{sample_id}.json"

        # 跳过已存在的配置
        if config_path.exists():
            print(f"[跳过] 配置已存在: {config_path.name}")
            continue

        config = {
            "sample_id": sample_id,
            "video_file": video_path.name,
            "utterances": [],
            "metadata": get_metadata(sample_id),
        }

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        print(f"[创建] {config_path.name}")
        created += 1

    print(f"[完成] 创建了 {created} 个配置文件")
    print(f"[下一步] 运行 python run_dataset_demo.py 进行转码")


if __name__ == "__main__":
    main()
