from pydantic import BaseModel

class TaskRequest(BaseModel):
    record_id: int
    minio_bucket: str
    minio_key: str