import whisper
from .config import settings

# 懒加载，内部变量，避免import时加载模型，让第一次调用的时候再加载
_model = None
# 后续改进可用FastAPI 启动事件中加载模型（或者利用 Docker 的健康检查来预热）

def get_model():
    global _model
    if _model is None:
        print(f"[ASR] 正在加载 Whisper 模型:{settings.WHISPER_MODEL} ...")
        _model = whisper.load_model(settings.WHISPER_MODEL)
    return _model

# 转录音频文件，返回文本
def transcribe(file_path: str) -> str:
    try:
        model = get_model()
        # fp16=false 避免显存不足,兼容cpu推理
        # 需要传一个字符串类型的路径。，强制使用 FP32 (全精度)
        result = model.transcribe(file_path, fp16=False)
        # 去掉文字首尾的空格或换行符，让结果更干净
        return result["text"].strip()
    except Exception as e:
        print(f"[ASR] 转录失败: {e}")
        return ""
