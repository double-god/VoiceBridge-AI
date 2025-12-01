"""
音频清洗模块
- 降噪
- 静音切分
- 音量归一化
- 重采样
"""

import subprocess
from pathlib import Path


def clean_audio(
    input_path: str | Path,
    output_path: str | Path | None = None,
    sample_rate: int = 16000,
    normalize: bool = True,
    denoise: bool = True,
    remove_silence: bool = True,
    silence_threshold: str = "-40dB",
    min_silence_duration: float = 0.5,
) -> Path | None:
    """
    音频清洗：降噪 + 静音切分 + 归一化 + 重采样

    Args:
        input_path: 输入音频路径
        output_path: 输出路径，默认覆盖原文件
        sample_rate: 目标采样率 (Whisper 推荐 16000)
        normalize: 是否归一化音量
        denoise: 是否降噪
        remove_silence: 是否移除静音段
        silence_threshold: 静音阈值 (dB)
        min_silence_duration: 最小静音时长 (秒)

    Returns:
        输出文件路径，失败返回 None
    """
    input_path = Path(input_path)
    if not input_path.exists():
        print(f"   [错误] 文件不存在: {input_path}")
        return None

    # 默认输出到临时文件，成功后替换
    if output_path is None:
        output_path = input_path
    output_path = Path(output_path)

    # 使用临时文件避免覆盖问题
    temp_path = output_path.with_suffix(".tmp.wav")

    # 构建 ffmpeg 滤镜链
    filters = []

    # 1. 降噪 (使用 afftdn 滤镜)
    if denoise:
        # afftdn: FFT 降噪，nr=降噪强度(0-97)，nf=噪声底限
        filters.append("afftdn=nf=-25:nr=10")

    # 2. 移除静音段
    if remove_silence:
        # silenceremove: 移除开头和结尾的静音
        # start_periods=1: 移除开头静音
        # stop_periods=1: 移除结尾静音
        # start_threshold/stop_threshold: 静音阈值
        # start_silence/stop_silence: 保留的静音时长
        filters.append(
            f"silenceremove=start_periods=1:start_threshold={silence_threshold}"
            f":start_silence=0.1:stop_periods=1:stop_threshold={silence_threshold}"
            f":stop_silence=0.1"
        )

    # 3. 音量归一化
    if normalize:
        # loudnorm: EBU R128 响度归一化
        filters.append("loudnorm=I=-16:TP=-1.5:LRA=11")

    # 4. 重采样
    filters.append(f"aresample={sample_rate}")

    # 构建 ffmpeg 命令
    filter_str = ",".join(filters) if filters else "anull"

    cmd = [
        "ffmpeg",
        "-y",  # 覆盖输出
        "-i",
        str(input_path),
        "-af",
        filter_str,
        "-ar",
        str(sample_rate),
        "-ac",
        "1",  # 单声道
        "-c:a",
        "pcm_s16le",  # 16-bit PCM
        str(temp_path),
    ]

    try:
        print(f"   [清洗中] {input_path.name}...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )

        # 成功后移动临时文件
        temp_path.replace(output_path)
        print(f"   [完成] {output_path.name}")
        return output_path

    except subprocess.CalledProcessError as e:
        print(f"   [错误] 清洗失败: {e.stderr}")
        if temp_path.exists():
            temp_path.unlink()
        return None
    except FileNotFoundError:
        print("   [错误] 未找到 ffmpeg，请先安装")
        return None


def batch_clean_audio(
    input_dir: str | Path,
    output_dir: str | Path | None = None,
    pattern: str = "*.wav",
    **kwargs,
) -> list[Path]:
    """
    批量清洗音频

    Args:
        input_dir: 输入目录
        output_dir: 输出目录，默认原地处理
        pattern: 文件匹配模式
        **kwargs: 传递给 clean_audio 的参数

    Returns:
        成功处理的文件列表
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir) if output_dir else input_dir

    if output_dir != input_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

    audio_files = sorted(input_dir.glob(pattern))
    if not audio_files:
        print(f"   [警告] 未找到音频文件: {input_dir}/{pattern}")
        return []

    print(f"[开始] 批量清洗 {len(audio_files)} 个文件...")

    results = []
    for audio_path in audio_files:
        output_path = output_dir / audio_path.name
        result = clean_audio(audio_path, output_path, **kwargs)
        if result:
            results.append(result)

    print(f"[完成] 成功清洗 {len(results)}/{len(audio_files)} 个文件")
    return results


if __name__ == "__main__":
    # 测试用
    import sys

    if len(sys.argv) > 1:
        clean_audio(sys.argv[1])
    else:
        print("用法: python audio_cleaner.py <音频文件>")
