from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from .config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# 对应go的model.user
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(355), nullable=False)
    name = Column(String(100))
    age = Column(Integer)
    condition = Column(Text)
    habits = Column(Text)
    common_needs = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# 对应go的model.VoiceRecord
class VoiceRecord(Base):
    __tablename__ = "voice_records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    audio_url = Column(String(500))
    raw_text = Column(Text)
    refined_text = Column(Text)
    confidence = Column(String(10))
    decision = Column(String(20))
    reason = Column(Text)
    tts_url = Column(String(500))
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # 上传-> 处理中->已完成->失败


# 对应go:model.AnalysisResult
class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    id = Column(Integer, primary_key=True)
    voice_record_id = Column(Integer)
    transcript = Column(Text)
    analysis_data = Column(Text)
    confidence = Column(Float)
    decision = Column(String)
    tts_audio_url = Column(String)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def update_record_status(db, record_id: int, status: str, **kwargs):
    """
    更新语音记录
    Args:
        db: 数据库会话
        record_id: 记录ID
        status: 新状态pending/processing_asr/processing_llm/processing_tts/completed/failed
        kwargs: 其他字段更新
    """
    record = db.query(VoiceRecord).filter(VoiceRecord.id == record_id).first()
    if record:
        record.status = status
        record.updated_at = datetime.utcnow()
        for key, value in kwargs.items():
            if hasattr(record, key):
                setattr(record, key, value)
        db.commit()
        print(f"记录 {record_id} 状态更新为 {status}")
        return record
    return None


def get_user_profile(db, user_id: int) -> dict:
    """
    获取用户画像
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        return {
            "name": user.name or user.username,
            "age": user.age or "未知",
            "condition": user.condition or "未知",
            "habits": user.habits or "未知",
            "common_needs": user.common_needs.split(",") if user.common_needs else [],
        }
    return {}


def get_record(db, record_id: int) -> VoiceRecord | None:
    """
    获取语音记录
    """
    return db.query(VoiceRecord).filter(VoiceRecord.id == record_id).first()


def save_analysis_result(
    db,
    voice_record_id: int,
    transcript: str,
    analysis_data: str,
    confidence: float,
    decision: str,
    tts_audio_url: str,
) -> AnalysisResult:
    """
    保存分析结果到数据库

    Args:
        db: 数据库会话
        voice_record_id: 语音记录 ID
        transcript: ASR 转录文本
        analysis_data: LLM 分析结果 JSON
        confidence: 置信度
        decision: 决策 (accept/boundary/reject)
        tts_audio_url: TTS 音频 URL

    Returns:
        保存的分析结果对象
    """
    result = AnalysisResult(
        voice_record_id=voice_record_id,
        transcript=transcript,
        analysis_data=analysis_data,
        confidence=confidence,
        decision=decision,
        tts_audio_url=tts_audio_url,
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    print(f"[DB] 保存分析结果 voice_record_id={voice_record_id}")
    return result
