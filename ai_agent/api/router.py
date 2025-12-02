from fastapi import APIRouter, BackgroundTasks
from schemas.task import TaskRequest
from services.pipeline import run_pipeline

router = APIRouter()

@router.post("/process")
async def process_voice(task: TaskRequest, background_tasks: BackgroundTasks):
    """
    接收Go后端语音处理请求,异步运行处理流水线。

    Args:
        task: 包含 record_id、minio_bucket 和 minio_key 的任务请求
        background_tasks是FastAPI 的后台任务管理器

    Returns:
        任务接收确认信息
    """
    background_tasks.add_task(run_pipeline, task.record_id, task.minio_key)
    return {"msg": f"任务{task.record_id} 已接收，正在后台处理。"}