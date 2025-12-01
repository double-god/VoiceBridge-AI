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
            "metadata": {
                "description": f"视频: {video_path.name}",
                "source": "local",
            },
        }

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        print(f"[创建] {config_path.name}")
        created += 1

    print(f"[完成] 创建了 {created} 个配置文件")
    print(f"[下一步] 运行 python run_dataset_demo.py 进行转码")


if __name__ == "__main__":
    main()
