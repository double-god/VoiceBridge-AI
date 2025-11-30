"""
数据加载器抽象基类
为未来接入不同数据源预留扩展接口
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass
class Sample:
    """
    单个数据样本
    包含音频路径和对应的转写信息
    """

    sample_id: str  # 样本唯一标识
    audio_path: Path  # 音频文件路径 (WAV)
    transcript: list[dict]  # 转写内容 [{speaker, text, start_ms, end_ms}, ...]
    metadata: dict | None = None  # 其他元数据


class BaseLoader(ABC):
    """
    数据加载器抽象基类

    子类需要实现:
        - load(): 加载所有样本
        - __len__(): 返回样本数量
        - __iter__(): 迭代器

    Usage:
        loader = SomeLoader(data_dir="path/to/data")
        for sample in loader:
            print(sample.sample_id, sample.audio_path)
    """

    def __init__(self, data_dir: str | Path):
        """
        Args:
            data_dir: 数据目录路径
        """
        self.data_dir = Path(data_dir)
        self._samples: list[Sample] = []
        self._loaded = False

    @abstractmethod
    def load(self) -> list[Sample]:
        """
        加载数据，子类必须实现

        Returns:
            样本列表
        """
        pass

    def _ensure_loaded(self):
        """确保数据已加载"""
        if not self._loaded:
            self._samples = self.load()
            self._loaded = True

    def __len__(self) -> int:
        self._ensure_loaded()
        return len(self._samples)

    def __iter__(self) -> Iterator[Sample]:
        self._ensure_loaded()
        return iter(self._samples)

    def __getitem__(self, index: int) -> Sample:
        self._ensure_loaded()
        return self._samples[index]

    def get_by_id(self, sample_id: str) -> Sample | None:
        """根据 ID 获取样本"""
        self._ensure_loaded()
        for sample in self._samples:
            if sample.sample_id == sample_id:
                return sample
        return None
