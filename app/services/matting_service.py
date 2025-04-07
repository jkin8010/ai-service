import torch
from PIL import Image
import torchvision.transforms as transforms
import numpy as np
from typing import Tuple, Optional, Dict, Any
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
from models.BiRefNet.birefnet import BiRefNet
from models.BiRefNet.BiRefNet_config import BiRefNetConfig


class MattingService:
    MODEL_MAPPING = {
        "default": "birefnet",
        "hr": "birefnet-hr",
        "portrait": "birefnet-portrait",
    }

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # 注册所有模型
        from app.models import __init__  # 确保模型已注册

    def _load_model(self, model_path: str) -> BiRefNet:
        """加载模型"""
        config = BiRefNetConfig(bb_pretrained=True)
        model = BiRefNet(config=config)

        # 确保模型文件存在
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"模型文件不存在: {model_path}")

        # 加载预训练权重
        state_dict = torch.load(model_path, map_location=self.device)
        model.load_state_dict(state_dict)

        # 将模型移到设备上并设置为评估模式
        model = model.to(self.device)
        model.eval()
        return model

    def preprocess_image(self, image: Image.Image, size: int = 1024) -> torch.Tensor:
        """预处理输入图像"""
        transform = transforms.Compose(
            [
                transforms.Resize((size, size)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

        image = image.convert("RGB")
        image = transform(image)
        return image.unsqueeze(0)

    def postprocess_mask(
        self, mask: torch.Tensor, original_size: Tuple[int, int]
    ) -> Image.Image:
        """后处理预测的mask"""
        mask = mask.squeeze().cpu().numpy()
        mask = (mask > 0.5).astype(np.uint8) * 255
        mask = Image.fromarray(mask).resize(original_size, Image.BILINEAR)
        return mask

    async def process_image(self, image: Image.Image) -> Image.Image:
        """处理单张图片"""
        original_size = image.size

        # 预处理输入
        input_tensor = self.preprocess_image(image)
        input_tensor = input_tensor.to(self.device)

        # 模型推理
        with torch.no_grad():
            output = self.model(input_tensor)

        # 后处理输出
        mask = self.postprocess_mask(output, original_size)
        return mask

    async def create_matting_task(
        self, file_url: str, model_type: str = "default"
    ) -> Dict[str, Any]:
        """创建抠图任务"""
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
