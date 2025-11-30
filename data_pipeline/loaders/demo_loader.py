"""
Demo 数据加载器
支持从 JSON 配置加载，并自动转码视频
"""

import json
from pathlib import Path

from .base import BaseLoader, Sample
from ..processors.converter import convert_mp4_to_wav


class DemoLoader(BaseLoader):
    """
    Demo 数据加载器

    支持两种模式:
    1. 纯数据模式: data_dir 下有 .wav + .json 文件
    2. 转码模式: 指定 video_dir，自动将 MP4 转为 WAV

    目录结构 (纯数据模式):
        data_dir/
        ├── sample1.wav
        ├── sample1.json
        └── ...

    JSON 格式:
        {
            "sample_id": "sample1",
            "video_file": "sample1.mp4",  // 可选，用于转码模式
            "utterances": [...],
            "metadata": {...}
        }
    """

    def __init__(
        self,
        data_dir: str | Path,
        video_dir: str | Path | None = None,  # 可选：视频源目录
    ):
        super().__init__(data_dir)
        self.video_dir = Path(video_dir) if video_dir else None

    def load(self) -> list[Sample]:
        """加载 demo 数据"""
        samples = []

        if not self.data_dir.exists():
            print(f"   [错误] 数据目录不存在: {self.data_dir}")
            return samples

        # 查找所有 JSON 文件
        json_files = sorted(self.data_dir.glob("*.json"))

        if not json_files:
            print(f"   [警告] 未找到 JSON 配置文件: {self.data_dir}")
            return samples

        for json_path in json_files:
            try:
                sample = self._load_sample(json_path)
                if sample:
                    samples.append(sample)
            except Exception as e:
                print(f"   [错误] 加载失败 {json_path.name}: {e}")

        print(f"   [完成] 加载 {len(samples)} 个样本")
        return samples

    def _load_sample(self, json_path: Path) -> Sample | None:
        """加载单个样本"""
        # 读取 JSON
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        sample_id = data.get("sample_id", json_path.stem)
        audio_path = json_path.with_suffix(".wav")

        # 如果音频不存在，尝试从视频转码
        if not audio_path.exists():
            video_file = data.get("video_file")
            if video_file and self.video_dir:
                video_path = self.video_dir / video_file
                if video_path.exists():
                    print(f"   [转码] {video_file} -> {audio_path.name}")
                    result = convert_mp4_to_wav(video_path, audio_path)
                    if not result:
                        print(f"   [错误] 转码失败: {video_file}")
                        return None
                else:
                    print(f"   [警告] 视频文件不存在: {video_path}")
                    return None
            else:
                print(f"   [警告] 缺少音频文件: {audio_path.name}")
                return None

        # 构建样本
        return Sample(
            sample_id=sample_id,
            audio_path=audio_path,
            transcript=data.get("utterances", []),
            metadata=data.get("metadata"),
        )

    @staticmethod
    def create_sample_json(
        output_path: Path,
        sample_id: str,
        utterances: list[dict],
        metadata: dict | None = None,
    ):
        """
        创建样本 JSON 文件（工具方法）

        Args:
            output_path: 输出路径
            sample_id: 样本 ID
            utterances: 话语列表
            metadata: 元数据
        """
        data = {
            "sample_id": sample_id,
            "utterances": utterances,
            "metadata": metadata or {},
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"   [完成] 创建 JSON: {output_path}")
