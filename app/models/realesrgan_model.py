import torch
from PIL import Image
import numpy as np
from typing import Dict, Optional
import io
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from app.core.model_registry import BaseModel
from models.RealESRGAN.model import RealESRGAN


class RealESRGANModel(BaseModel):
    # 模型配置
    MODEL_CONFIG = {
        "x2": {
            "path": os.path.join(
                project_root, "models/RealESRGAN/RealESRGAN_x2plus.pth"
            ),
            "scale": 2,
        },
        "x4": {
            "path": os.path.join(
                project_root, "models/RealESRGAN/RealESRGAN_x4plus.pth"
            ),
            "scale": 4,
        },
        "x8": {
            "path": os.path.join(
                project_root, "models/RealESRGAN/RealESRGAN_x8plus.pth"
            ),
            "scale": 8,
        },
    }

    def __init__(self, model_type: str = "x4"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_type = model_type

        # 获取模型配置
        self.config = self.MODEL_CONFIG.get(model_type)
        if not self.config:
            raise ValueError(f"不支持的模型类型: {model_type}")

        self.scale = self.config["scale"]
        self.model = self._load_model()

    def _load_model(self) -> RealESRGAN:
        """加载模型"""
        model_path = self.config["path"]
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"模型文件不存在: {model_path}")

        # 创建模型实例
        model = RealESRGAN(device=self.device, scale=self.scale)

        # 加载权重
        model.load_weights(model_path, download=False)

        return model

    def preprocess(self, input_data: bytes) -> bytes:
        """预处理输入图像"""
        # 读取图像
        image = Image.open(io.BytesIO(input_data)).convert("RGB")

        # 保存原始大小
        self.original_size = image.size

        # 转换为字节
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    def predict(self, input_data: bytes) -> Dict:
        """执行模型推理"""
        # 将字节数据转换为图像
        image = Image.open(io.BytesIO(input_data)).convert("RGB")

        # 执行推理
        sr_image = self.model.predict(image)

        # 转换为字节
        buffer = io.BytesIO()
        sr_image.save(buffer, format="PNG")

        return {
            "result_image": buffer.getvalue(),
        }

    def postprocess(self, output_data: Dict) -> Dict:
        """后处理预测结果"""
        # 对于超分辨率任务，预测结果已经是最终结果
        return output_data
