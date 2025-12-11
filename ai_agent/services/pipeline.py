import os
import json
import tempfile
import asyncio

from core import asr_whisper, llm_reasoning, tts_cosy, storage
from core.database import (
    SessionLocal,
    update_record_status,
    get_user_profile,
    save_analysis_result,
)


async def process_voice_record(record_id: int, minio_key: str, user_id: int) -> dict:
    """
    处理语音流程
    流程:
    1. 更新状态为 processing_asr
    2. 从 MinIO 下载音频
    3. 执行 ASR
    4. 更新状态为 processing_llm
    5. 执行 LLM 推理
    6. 更新状态为 processing_tts
    7. 执行 TTS 合成 (CosyVoice)
    8. 上传 TTS 音频到 MinIO
    9. 更新状态为 completed, 保存所有结果

    Args:
        record_id: 语音记录 ID
        minio_key: MinIO 中的音频文件 key
        user_id: 用户 ID

    Returns:
        处理结果字典
    """
    db = SessionLocal()
    temp_files = []  # 记录临时文件, 最后清理

    try:
        # 更新状态
        update_record_status(db, record_id, "processing_asr")
        print(f"[Pipeline] 开始处理记录 {record_id}")

        # 从 MinIO 下载音频
        local_audio_path = storage.download_file(minio_key)
        temp_files.append(local_audio_path)

        # 执行 ASR (使用线程池避免阻塞主循环)
        print(f"[Pipeline] 执行 ASR...")
        raw_text = await asyncio.to_thread(asr_whisper.transcribe, local_audio_path)
        print(f"[Pipeline] ASR 结果: {raw_text}")

        # 更新状态, 准备 LLM
        update_record_status(db, record_id, "processing_llm", raw_text=raw_text)

        # 获取用户画像, 执行 LLM 推理
        print(f"[Pipeline] 执行 LLM 推理...")
        user_profile = get_user_profile(db, user_id)
        llm_result = llm_reasoning.infer_intent(raw_text, user_profile)
        print(f"[Pipeline] LLM 结果: {llm_result}")

        refined_text = llm_result.get("refined_text", raw_text)
        confidence = llm_result.get("confidence", 0)
        decision = llm_result.get("decision", "reject")
        reason = llm_result.get("reason", "")
        response_text = llm_result.get("response_text", refined_text)  # 获取响应文本

        # 更新状态, 准备 TTS
        update_record_status(
            db,
            record_id,
            "processing_tts",
            refined_text=refined_text,
            confidence=str(confidence),
            decision=decision,
            reason=reason,
        )

        # 执行 TTS (所有决策类型都生成语音响应)
        print(f"[Pipeline] 执行 TTS (response_text: {response_text[:50]}...)...")
        temp_dir = tempfile.mkdtemp()
        tts_local_path = await tts_cosy.tts_edge(
            response_text, temp_dir
        )  # 使用 response_text
        temp_files.append(tts_local_path)

        # 上传 TTS 到 MinIO
        tts_object_name = f"tts/{record_id}_{os.path.basename(tts_local_path)}"
        tts_url = storage.upload_file(tts_local_path, tts_object_name)
        print(f"[Pipeline] TTS 上传完成: {tts_url}")

        # 保存分析结果
        save_analysis_result(
            db=db,
            voice_record_id=record_id,
            asr_text=raw_text,
            refined_text=refined_text,
            response_text=response_text,  # 新增 response_text
            confidence=float(confidence),
            decision=decision,
            tts_audio_url=tts_url,
        )

        # 完成, 更新最终状态
        update_record_status(db, record_id, "completed", tts_url=tts_url)
        print(f"[Pipeline] 记录 {record_id} 处理完成!")

        return {
            "record_id": record_id,
            "status": "completed",
            "raw_text": raw_text,
            "refined_text": refined_text,
            "confidence": confidence,
            "decision": decision,
            "reason": reason,
            "tts_url": tts_url,
        }

    except Exception as e:
        # 出错时更新状态
        print(f"[Pipeline] 处理失败: {e}")
        import traceback

        traceback.print_exc()

        try:
            # 回滚事务，避免 PendingRollbackError
            db.rollback()
            update_record_status(db, record_id, "error", reason=str(e))
        except Exception as db_error:
            print(f"[Pipeline] 更新错误状态失败: {db_error}")
        raise

    finally:
        # 清理临时文件
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    parent_dir = os.path.dirname(temp_file)
                    if parent_dir.startswith(tempfile.gettempdir()) and not os.listdir(
                        parent_dir
                    ):
                        os.rmdir(parent_dir)
            except Exception:
                pass
        db.close()
