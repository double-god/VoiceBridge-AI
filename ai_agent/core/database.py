from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# 对应go的model.user
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    name = Column(String)
    age = Column(Integer)
    condition = Column(Text)
    habits = Column(Text)
    common_needs = Column(Text)


# 对应go的model.VoiceRecord
class VoiceRecord(Base):
    __tablename__ = "voice_records"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    minio_bucket = Column(String)
    minio_key = Column(String)
    status = Column(String)
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
