"""
MP4 -> WAV 音频转换器
使用 ffmpeg 提取音频轨道
"""

import subprocess
from pathlib import Path


def convert_mp4_to_wav(
    input_path: str | Path,
    output_path: str | Path,
    sample_rate: int = 16000,  # 采样率 16kHz
    channels: int = 1,  # 单声道
    skip_existing: bool = True,  # 跳过已存在文件
) -> Path | None:
    """
    将 MP4 视频转换为 WAV 音频

    Args:
        input_path: 输入 MP4 文件路径
        output_path: 输出 WAV 文件路径
        sample_rate: 采样率，默认 16000 Hz
        channels: 声道数，默认单声道
        skip_existing: 是否跳过已存在的文件

    Returns:
        输出文件路径，失败返回 None
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        print(f"   [错误] 输入文件不存在: {input_path}")
        return None

    # 跳过已存在文件
    if skip_existing and output_path.exists():
        print(f"   [跳过] 音频已存在: {output_path.name}")
        return output_path

    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"   [转码中] {input_path.name} -> {output_path.name}...")

    # ffmpeg 命令
    cmd = [
        "ffmpeg",
        "-i",
        str(input_path),  # 输入文件
        "-vn",  # 不要视频
        "-acodec",
        "pcm_s16le",  # 16-bit PCM 编码
        "-ar",
        str(sample_rate),  # 采样率
        "-ac",
        str(channels),  # 声道数
        "-y",  # 覆盖已存在的文件
        "-loglevel",
        "error",  # 静默模式
        str(output_path),
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"   [完成] {output_path.name}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"   [错误] 转码失败: {e}")
        return None


def batch_convert(input_dir: str | Path, output_dir: str | Path) -> list[Path]:
    """
    批量转换目录下所有 MP4 文件

    Args:
        input_dir: 输入目录
        output_dir: 输出目录

    Returns:
        所有成功转换的输出文件路径列表
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    mp4_files = list(input_dir.glob("*.mp4")) + list(input_dir.glob("*.MP4"))

    if not mp4_files:
        print(f"   [警告] 未找到 MP4 文件: {input_dir}")
        return []

    print(f"   [信息] 找到 {len(mp4_files)} 个视频文件")

    results = []
    for mp4_file in mp4_files:
        wav_file = output_dir / f"{mp4_file.stem}.wav"
        result = convert_mp4_to_wav(mp4_file, wav_file)
        if result:
            results.append(result)

    return results