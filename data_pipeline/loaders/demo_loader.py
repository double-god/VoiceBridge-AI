"""
Demo 数据加载器
针对手头 3 个视频的加载实现
"""

import json
from pathlib import Path

from .base import BaseLoader, Sample


class DemoLoader(BaseLoader):
    """
    Demo 数据加载器

    期望的目录结构:
        data_dir/
        ├── sample1.wav
        ├── sample1.json
        ├── sample2.wav
        ├── sample2.json
        └── ...

    JSON 格式:
        {
            "sample_id": "sample1",
            "utterances": [
                {"speaker": "PAR", "text": "hello", "start_ms": 0, "end_ms": 1000},
                ...
            ],
            "metadata": {...}
        }
    """

    def load(self) -> list[Sample]:
        """加载 demo 数据"""
        samples = []

        if not self.data_dir.exists():
            print(f"数据目录不存在: {self.data_dir}")
            return samples

        # 查找所有 JSON 文件
        json_files = sorted(self.data_dir.glob("*.json"))

        for json_path in json_files:
            try:
                sample = self._load_sample(json_path)
                if sample:
                    samples.append(sample)
            except Exception as e:
                print(f"加载失败 {json_path.name}: {e}")

        print(f"加载完成: {len(samples)} 个样本")
        return samples

    def _load_sample(self, json_path: Path) -> Sample | None:
        """加载单个样本"""
        # 读取 JSON
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        sample_id = data.get("sample_id", json_path.stem)

        # 查找对应的音频文件
        audio_path = json_path.with_suffix(".wav")
        if not audio_path.exists():
            print(f"缺少音频文件: {audio_path.name}")
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

        print(f"创建 JSON: {output_path}")
