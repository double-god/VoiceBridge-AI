from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from services.pipeline import process_voice_record

router = APIRouter()


class ProcessRequest(BaseModel):
    """处理请求的模型"""

    record_id: int
    user_id: int
    minio_key: str


class ProcessResponse(BaseModel):
    """处理响应的模型"""

    message: str
    record_id: int


@router.post("/process", response_model=ProcessResponse)
async def process_voice(request: ProcessRequest, background_tasks: BackgroundTasks):
    """
    接收 Go 后端语音处理请求, 异步处理语音记录

    - Go 后端上传语音文件到 MinIO 后, 调用此接口
    - 返回后立即开始后台处理
    - 前端 SSE 轮询 Go 后端获取处理状态和结果
    """
    # 添加到后台任务队列
    background_tasks.add_task(
        process_voice_record, request.record_id, request.minio_key, request.user_id
    )

    return ProcessResponse(message="处理任务已提交", record_id=request.record_id)


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "ai_agent"}
