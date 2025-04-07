import torch
from PIL import Image
import torchvision.transforms as transforms
import numpy as np
from typing import Dict, Tuple, Optional
import io
import os
import sys
from pathlib import Path
from safetensors.torch import load_file

# 添加项目根目录到Python路径
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from app.core.model_registry import BaseModel
from models.BiRefNet.birefnet import BiRefNet
from models.BiRefNet.BiRefNet_config import BiRefNetConfig


class BiRefNetModel(BaseModel):
    # 模型配置
    MODEL_CONFIG = {
        "default": {
            "path": os.path.join(project_root, "models/BiRefNet/model.safetensors"),
            "size": 1024,  # 默认输入大小
        },
        "hr": {
            "path": os.path.join(project_root, "models/BiRefNet_HR/model.safetensors"),
            "size": 2048,  # HR版本使用更大的输入尺寸
        },
        "portrait": {
            "path": os.path.join(
                project_root, "models/BiRefNet_portrait/model.safetensors"
            ),
            "size": 1024,  # 人像版本使用标准尺寸
        },
    }

    def __init__(self, model_type: str = "default"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_type = model_type

        # 获取模型配置
        self.config = self.MODEL_CONFIG.get(model_type)
        if not self.config:
            raise ValueError(f"不支持的模型类型: {model_type}")

        self.size = self.config["size"]
        self.model = self._load_model()

    def _load_model(self) -> BiRefNet:
        """加载模型"""
        model_path = self.config["path"]
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"模型文件不存在: {model_path}")

        # 禁用预训练权重加载
        config = BiRefNetConfig(bb_pretrained=False)
        model = BiRefNet(config=config)

        # 使用safetensors加载模型权重
        state_dict = load_file(model_path)  # 先加载到CPU
        model.load_state_dict(state_dict)

        # 将模型移到设备上并设置为评估模式
        model = model.to(self.device)
        model.eval()
        return model

    def preprocess(self, input_data: bytes) -> bytes:
        """预处理输入图像"""
        # 读取图像
        image = Image.open(io.BytesIO(input_data)).convert("RGB")

        # 预处理
        transform = transforms.Compose(
            [
                transforms.Resize((self.size, self.size)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

        # 保存原始大小
        self.original_size = image.size

        # 转换图像
        image_tensor = transform(image)
        image_tensor = image_tensor.unsqueeze(0)

        # 转换为字节
        buffer = io.BytesIO()
        torch.save(image_tensor, buffer)
        return buffer.getvalue()

    def predict(self, input_data: bytes) -> Dict:
        """执行模型推理"""
        # 将字节数据转换为图像
        image = Image.open(io.BytesIO(input_data)).convert("RGB")

        # 预处理图像
        transform = transforms.Compose(
            [
                transforms.Resize((self.size, self.size)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

        # 转换图像
        input_tensor = transform(image)
        input_tensor = input_tensor.unsqueeze(0)
        input_tensor = input_tensor.to(self.device)

        # 保存原始大小
        self.original_size = image.size

        # 执行推理
        with torch.no_grad():
            output = self.model(input_tensor)

        # 后处理
        return self.postprocess(output)

    def postprocess(self, output_data: torch.Tensor) -> Dict:
        """后处理预测的mask"""
        # 处理输出
        if isinstance(output_data, list):
            # 如果输出是列表，取第一个元素
            output_data = output_data[0]

        # 确保输出是tensor
        if not isinstance(output_data, torch.Tensor):
            raise ValueError(f"Unexpected output type: {type(output_data)}")

        # 处理输出
        mask = output_data.squeeze().cpu().numpy()
        mask = (mask > 0.5).astype(np.uint8) * 255

        # 调整大小
        mask = Image.fromarray(mask).resize(self.original_size, Image.BILINEAR)

        # 转换为字节
        buffer = io.BytesIO()
        mask.save(buffer, format="PNG")

        return {
            "mask_image": buffer.getvalue(),
            "result_image": buffer.getvalue(),  # 对于matting任务，mask就是结果
        }
