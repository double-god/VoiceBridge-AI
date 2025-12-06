"""
CosyVoice TTS Service - 基于阿里 ModelScope
使用离线模型，无需代理，支持中英文合成
采用延迟加载策略，避免启动时导入问题
"""

import os
import uuid
import torch
import torchaudio


class TTSService:
    """CosyVoice 语音合成服务 - 延迟加载版本"""

    _instance = None
    _initialized = False

    def __new__(cls):
        """单例模式 - 全局只初始化一次"""
        if cls._instance is None:
            cls._instance = super(TTSService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化 TTS 服务 - 模型延迟加载"""
        if TTSService._initialized:
            return

        print("[TTS] CosyVoice 服务已就绪 (模型将在首次调用时加载)")
        self.model_dir = None
        self.inference = None
        TTSService._initialized = True

    def _ensure_loaded(self):
        """确保模型已加载 - 延迟初始化，首次调用时才加载"""
        if self.inference is not None:
            return  # 已加载

        print("[TTS] 正在初始化 CosyVoice (首次运行会自动下载模型，约3-5GB)...")

        # 指定模型保存目录
        cache_dir = "/app/models"
        model_dir = os.path.join(cache_dir, "iic/CosyVoice-300M-SFT")

        try:
            # 运行时动态导入，避免启动时就报错
            from cosyvoice.cli.cosyvoice import CosyVoice

            # 检查模型是否已下载
            if not os.path.exists(model_dir):
                print("[TTS] 模型不存在，正在从 ModelScope 下载...")
                from modelscope import snapshot_download

                model_dir = snapshot_download(
                    "iic/CosyVoice-300M-SFT", cache_dir=cache_dir
                )
            else:
                print(f"[TTS] 使用已下载的模型: {model_dir}")

            # 初始化 CosyVoice
            print(f"[TTS] 正在加载 CosyVoice 模型...")
            self.inference = CosyVoice(model_dir)
            self.model_dir = model_dir

            device_info = "GPU" if torch.cuda.is_available() else "CPU"
            print(f"[TTS] ✅ CosyVoice 加载成功！运行设备: {device_info}")

        except Exception as e:
            print(f"[TTS] ❌ CosyVoice 初始化失败: {e}")
            import traceback

            traceback.print_exc()
            raise e

    async def synthesize(self, text: str, output_file: str) -> str:
        """
        合成语音并保存到文件

        Args:
            text: 要合成的文本
            output_file: 输出文件路径 (.wav)

        Returns:
            生成的音频文件路径
        """
        # 确保模型已加载
        self._ensure_loaded()

        print(f"[TTS] 正在合成: {text[:50]}...")

        try:
            # 使用 CosyVoice 的 inference_sft 方法进行零样本合成
            # 对于中文文本使用中文音色，英文文本使用英文音色
            output = self.inference.inference_sft(text, "中文女")

            # output 是一个生成器，遍历获取音频
            audio_data = []
            for audio_chunk in output:
                audio_data.append(audio_chunk["tts_speech"])

            # 合并音频数据
            if audio_data:
                audio_tensor = torch.cat(audio_data, dim=1)

                # 保存为 WAV 文件 (使用 soundfile backend)
                torchaudio.save(output_file, audio_tensor, 22050, backend="soundfile")
                print(f"[TTS] ✅ 合成完成: {output_file}")
                return output_file
            else:
                raise ValueError("没有生成音频数据")

        except Exception as e:
            print(f"[TTS] ❌ 语音合成出错: {e}")
            import traceback

            traceback.print_exc()
            raise e


# 全局单例实例
_tts_service = None


def get_tts_service() -> TTSService:
    """获取 TTS 服务单例"""
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service


async def tts_edge(text: str, output_dir: str) -> str:
    """
    兼容旧接口: 用CosyVoice替换Edge TTS

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

    # 使用 CosyVoice 合成
    tts = get_tts_service()
    return await tts.synthesize(text, output_path)


async def tts_to_path(text: str, output_path: str) -> str:
    """
    兼容旧接口: 用CosyVoice替换Edge TTS

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

    # 使用 CosyVoice 合成
    tts = get_tts_service()
    return await tts.synthesize(text, output_path)
