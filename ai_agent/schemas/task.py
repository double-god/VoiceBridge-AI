# 定义一个 Schema (TaskRequest)，里面只包含允许用户传递的字段（record_id, bucket, key）
from pydantic import BaseModel

class TaskRequest(BaseModel):
    record_id: int
    minio_bucket: str
    minio_key: str