from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from .config import settings

DATABASE_URL = settings.DATABASE_URL

# 建立连接池，先ping一下连接
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
# 创建会话类，防止误删数据
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# 对应go的model.user
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # 字段名改为 password,匹配 Go 模型
    role = Column(String(20), default="patient")
    name = Column(String(100))
    age = Column(Integer)
    condition = Column(Text)
    habits = Column(Text)
    common_needs = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)


# 对应go的model.VoiceRecord
class VoiceRecord(Base):
    __tablename__ = "voice_records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    minio_bucket = Column(String(100), nullable=False)
    minio_key = Column(String(255), nullable=False)
    duration = Column(Integer, nullable=False, default=0)
    audio_url = Column(String(500))
    raw_text = Column(Text)
    refined_text = Column(Text)
    confidence = Column(String(10))
    decision = Column(String(20))
    reason = Column(Text)
    tts_url = Column(String(500))
    status = Column(String(50), default="uploaded")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    # 状态流转: uploaded->processing_asr->processing_llm->processing_tts->completed->failed


# 对应go:model.AnalysisResult
class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    id = Column(Integer, primary_key=True)
    voice_record_id = Column(Integer)
    asr_text = Column(Text)
    refined_text = Column(Text)
    response_text = Column(Text, nullable=True)  # 新增: 根据 decision 生成的响应文本
    confidence = Column(Float)
    decision = Column(String)
    tts_audio_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

# 获取数据库会话
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
        status: 新状态pending/processing_asr/processing_llm/processing_tts/completed/failed/error
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
    asr_text: str,
    refined_text: str,
    response_text: str,
    confidence: float,
    decision: str,
    tts_audio_url: str,
) -> AnalysisResult:
    """
    保存分析结果到数据库 (如果已存在则更新)

    Args:
        db: 数据库会话
        voice_record_id: 语音记录 ID
        asr_text: ASR 转录文本
        refined_text: LLM 精炼后的文本
        response_text: 根据 decision 生成的响应文本
        confidence: 置信度
        decision: 决策 (accept/boundary/reject)
        tts_audio_url: TTS 音频 URL

    Returns:
        保存的分析结果对象
    """
    # 检查是否已存在
    result = (
        db.query(AnalysisResult)
        .filter(AnalysisResult.voice_record_id == voice_record_id)
        .first()
    )

    if result:
        # 更新已有记录
        result.asr_text = asr_text
        result.refined_text = refined_text
        result.response_text = response_text
        result.confidence = confidence
        result.decision = decision
        result.tts_audio_url = tts_audio_url
        print(f"[DB] 更新分析结果 voice_record_id={voice_record_id}")
    else:
        # 创建新记录
        result = AnalysisResult(
            voice_record_id=voice_record_id,
            asr_text=asr_text,
            refined_text=refined_text,
            response_text=response_text,
            confidence=confidence,
            decision=decision,
            tts_audio_url=tts_audio_url,
        )
        db.add(result)
        print(f"[DB] 保存分析结果 voice_record_id={voice_record_id}")

    db.commit()
    db.refresh(result)
    return result
