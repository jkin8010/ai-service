from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from typing import Dict, Any
import uuid
from app.services.task_service import task_service
from app.core.model_registry import model_registry
from app.utils.minio_client import minio_client

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    上传图片文件到MinIO

    Args:
        file: 要上传的图片文件

    Returns:
        包含文件URL的字典

    Raises:
        HTTPException: 当文件类型不支持时抛出400错误
    """
    try:
        # 验证文件类型
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file.content_type}，仅支持图片文件",
            )

        # 读取文件内容
        file_content = await file.read()

        # 上传到MinIO
        file_url = minio_client.upload_file(
            file_content, file.filename, file.content_type
        )

        return {"message": "文件上传成功", "file_url": file_url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_task(
    file_url: str, model_id: str, background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """创建新的AI处理任务"""
    try:
        # 检查模型是否存在
        if not model_registry.has_model(model_id):
            raise HTTPException(status_code=400, detail=f"Model {model_id} not found")

        # 创建任务
        task_id = str(uuid.uuid4())
        task = task_service.create_task(task_id, file_url, model_id)

        # 在后台处理任务
        background_tasks.add_task(task_service.process_task, task_id)

        return task
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}")
async def get_task_status(task_id: str) -> Dict[str, Any]:
    """获取任务状态"""
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}")
async def delete_task(task_id: str) -> Dict[str, Any]:
    """
    删除任务并停止处理

    Args:
        task_id: 任务ID

    Returns:
        删除结果
    """
    try:
        result = await task_service.delete_task(task_id)
        if not result:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"message": "Task deleted successfully", "task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
