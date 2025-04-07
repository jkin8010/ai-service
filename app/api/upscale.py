from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Literal
from app.services.task_service import task_service
from app.services.upscale_service import UpscaleService

router = APIRouter(prefix="/upscale", tags=["upscale"])

# 初始化服务
upscale_service = UpscaleService()


@router.post("/process")
async def create_upscale_task(
    file_url: str,
    background_tasks: BackgroundTasks,
    model_type: Literal["x2", "x4", "x8"] = "x4",
) -> Dict[str, Any]:
    """
    创建超分辨率任务

    Args:
        file_url: 图片URL
        background_tasks: 后台任务处理器
        model_type: 模型类型，可选值：
            - x2: 2倍超分辨率
            - x4: 4倍超分辨率
            - x8: 8倍超分辨率

    Returns:
        任务信息
    """
    try:
        # 创建任务
        task = await upscale_service.create_upscale_task(file_url, model_type)

        # 在后台处理任务
        background_tasks.add_task(task_service.process_task, task["task_id"])

        return task
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    获取任务状态

    Args:
        task_id: 任务ID

    Returns:
        任务状态信息
    """
    task = await upscale_service.get_task_status(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
