import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_ENV: str = os.getenv("APP_ENV", "development")

    # 数据库
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 5432))
    DB_USER: str = os.getenv("DB_USER", "")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "voicebridge")

    # MinIO
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ROOT_USER: str = os.getenv("MINIO_ROOT_USER", "")
    MINIO_ROOT_PASSWORD: str = os.getenv("MINIO_ROOT_PASSWORD", "")
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "voicebridge")
    MINIO_SECURE: bool = os.getenv("MINIO_SECURE", "false").lower() == "true"

    # AI Models
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")
    # llm api
    AI_AGENT_LLM_API_URL: str = os.getenv("AI_AGENT_LLM_API_URL", "")
    AI_AGENT_LLM_API_KEY: str = os.getenv("AI_AGENT_LLM_API_KEY", "")
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "qwen3-max")

    @property
    def DATABASE_URL(self) -> str:
        """构建数据库连接 URL"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = "../.env"  # 自动读取根目录 .env
        extra = "ignore"


settings = Settings()

# 拼接数据库 URL
DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
