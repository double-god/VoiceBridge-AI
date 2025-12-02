import edge_tts
import uuid
import os
import asyncio


async def tts_edge(text: str, output_dir: str) -> str:
    """
    用Edge TTS文本转换为语音并保存为 WAV 文件。

    Args:
        text: 要转换的文本
        output_dir: 输出目录

    Returns:
        生成的音频文件路径
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 生成唯一的文件名
    file_name = f"tts_{uuid.uuid4().hex}.wav"
    output_path = os.path.join(output_dir, file_name)

    # 创建Communicate 对象
    communicate = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")

    # 合成并保存为 WAV 文件
    await communicate.save(output_path)

    return output_path


async def tts_to_path(text: str, output_path: str) -> str:
    """
    用 Edge TTS 将文本转换为语音, 保存到指定路径
    Args:
        text: 要转换的文本
        output_path: 输出文件完整路径
    Returns:
        生成的音频文件路径
    """
    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # 创建 Communicate 对象
    communicate = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")

    # 合成并保存
    await communicate.save(output_path)

    print(f"[TTS] 合成完成: {output_path}")
    return output_path


def tts_sync(text: str, output_dir: str) -> str:
    """
    同步版本的TTS，方便非异步调用"""
    return asyncio.run(tts_edge(text, output_dir))
