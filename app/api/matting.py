from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Literal
from app.services.task_service import task_service
from app.services.matting_service import MattingService

router = APIRouter(prefix="/matting", tags=["matting"])

# 初始化服务
matting_service = MattingService()


@router.post("/process")
async def create_matting_task(
    file_url: str,
    background_tasks: BackgroundTasks,
    model_type: Literal["default", "hr", "portrait"] = "default",
) -> Dict[str, Any]:
    """
    创建抠图任务

    Args:
        file_url: 图片URL
        background_tasks: 后台任务处理器
        model_type: 模型类型，可选值：
            - default: 使用BiRefNet-matting模型
            - hr: 使用BiRefNet_HR-matting模型
            - portrait: 使用BiRefNet-portrait模型

    Returns:
        任务信息
    """
    try:
        # 创建任务
        task = await matting_service.create_matting_task(file_url, model_type)

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
    task = await matting_service.get_task_status(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
