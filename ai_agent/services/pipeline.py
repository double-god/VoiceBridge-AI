import os
import asyncio
from sqlalchemy.orm import Session
from ..core.database import SessionLocal, VoiceRecord, AnalysisResult, User
from ..core import asr_whisper, llm_reasoning, tts_edge, storage
from ..core.config import settings


async def run_pipeline(record_id: int, minio_key: str):
    """
    运行语音处理流水线，下载音频文件，进行转录、分析和文本转语音合成。
    """
    db: Session = SessionLocal()
    temp_audio = f"temp_{record_id}.wav"
    temp_tts = ""

    try:
        print(f"开始处理记录ID: {record_id}")

        # 获取用户画像
        record = db.query(VoiceRecord).filter(VoiceRecord.id == record_id).first()
        if not record:
            print(f"记录ID {record_id} 未找到")
            return

        user = db.query(User).filter(User.id == record.user_id).first()
        profile = {
            "name": user.name or user.username,
            "age": user.age or "未知",
            "condition": user.condition or "未知",
            "habits": user.habits or "未知",
            "common_needs": user.common_needs.split(",") if user.common_needs else [],
        }

        # ASR 转录
        _update_status(db, record, "处理中")
        storage.download_file(settings.MINIO_BUCKET, minio_key, temp_audio)
        raw_text = asr_whisper.transcribe_whisper(temp_audio)
        print(f"转录结果: {raw_text}")

        # LLM 分析
        _update_status(db, record, "分析中")
        ai_res = llm_reasoning.infer_intent(raw_text, profile)
        print(
            f" [LLM]{ai_res['decision']} - {ai_res['refined_text']} (置信度: {ai_res['confidence']})"
        )

        # TTS 合成
        tts_url = ""
        if ai_res["decision"] == "accept":
            _update_status(db, record, "合成中")
            temp_tts = await tts_edge.tts_edge(ai_res["refined_text"], ".")

            tts_key = f"tts/{os.path.basename(temp_tts)}"
            storage.upload_file(settings.MINIO_BUCKET, tts_key, temp_tts)

            # 构造相对路径
            tts_url = f"{settings.MINIO_BUCKET}/{tts_key}"

        # 保存分析结果
        analysis_result = AnalysisResult(
            record_id=record_id,
            decision=ai_res.get("decision", ""),
            refined_text=ai_res.get("refined_text", ""),
            confidence=ai_res.get("confidence", 0.0),
        )
        db.add(analysis_result)
        db.commit()

    except Exception as e:
        print(f"Task {record_id}失败: {e}")
        _update_status(db, record, "failed")

    finally:
        db.close()
        # 清理临时文件
        if os.path.exists(temp_audio):
            os.remove(temp_audio)
        if temp_tts and os.path.exists(temp_tts):
            os.remove(temp_tts)


def _update_status(db, record, status):
    record.status = status
    db.commit()
