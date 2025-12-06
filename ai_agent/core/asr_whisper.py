import whisper
from .config import settings

# 懒加载，避免import时加载模型，让第一次调用的时候再加载
_model = None


def get_model():
    global _model
    if _model is None:
        print(f"[ASR] 正在加载 Whisper 模型:{settings.WHISPER_MODEL} ...")
        _model = whisper.load_model(settings.WHISPER_MODEL)
    return _model


def transcribe(file_path: str) -> str:
    try:
        model = get_model()
        # fp16=false 避免显存不足,兼容cpu推理
        result = model.transcribe(file_path, fp16=False)
        return result["text"].strip()
    except Exception as e:
        print(f"[ASR] 转录失败: {e}")
        return ""
