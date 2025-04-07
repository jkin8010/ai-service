import torch
from PIL import Image
from typing import Dict, Any
import os
from pathlib import Path
import uuid
import sys

# 添加项目根目录到Python路径
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from app.core.model_registry import model_registry
from app.services.task_service import task_service


class UpscaleService:
    MODEL_MAPPING = {
        "x2": "realesrgan",
        "x4": "realesrgan",
        "x8": "realesrgan",
    }

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # 注册所有模型
        from app.models import __init__  # 确保模型已注册

    async def create_upscale_task(
        self, file_url: str, model_type: str = "x4"
    ) -> Dict[str, Any]:
        """创建超分辨率任务"""
        try:
            # 获取对应的模型ID
            model_id = self.MODEL_MAPPING.get(model_type)
            if not model_id:
                raise ValueError(f"不支持的模型类型: {model_type}")

            # 创建任务ID
            task_id = str(uuid.uuid4())

            # 创建任务记录
            task = task_service.create_task(task_id, file_url, model_id)

            # 创建模型实例
            model = model_registry.create_model_instance(model_id)
            if not model:
                raise ValueError(f"模型创建失败: {model_id}")

            # 设置模型类型
            model.model_type = model_type

            return task
        except Exception as e:
            raise Exception(f"Failed to create task: {str(e)}")

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        return task_service.get_task_status(task_id)
