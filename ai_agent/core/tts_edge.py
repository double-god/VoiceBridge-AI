import edge_tts
import uuid
import os
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