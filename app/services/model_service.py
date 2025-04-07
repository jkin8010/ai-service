import onnxruntime
import numpy as np
from PIL import Image
import io
from typing import Tuple
from app.core.config import settings


class ModelService:
    def __init__(self):
        self.session = onnxruntime.InferenceSession(settings.MODEL_PATH)
        self.input_size = settings.MODEL_INPUT_SIZE

    def preprocess_image(self, image_data: bytes) -> np.ndarray:
        """预处理图像"""
        # 读取图像
        image = Image.open(io.BytesIO(image_data))

        # 调整大小
        image = image.resize(self.input_size)

        # 转换为numpy数组
        image_array = np.array(image)

        # 归一化
        image_array = image_array.astype(np.float32) / 255.0

        # 添加批次维度
        image_array = np.expand_dims(image_array, axis=0)

        return image_array

    def postprocess_mask(self, mask: np.ndarray) -> Tuple[bytes, bytes]:
        """后处理分割结果"""
        # 获取原始mask
        mask = mask[0]  # 移除批次维度

        # 创建二值mask
        binary_mask = (mask > 0.5).astype(np.uint8) * 255

        # 转换为PIL图像
        mask_image = Image.fromarray(binary_mask)
        result_image = Image.fromarray((mask * 255).astype(np.uint8))

        # 转换为字节
        mask_buffer = io.BytesIO()
        result_buffer = io.BytesIO()

        mask_image.save(mask_buffer, format="PNG")
        result_image.save(result_buffer, format="PNG")

        return result_buffer.getvalue(), mask_buffer.getvalue()

    def predict(self, image_data: bytes) -> Tuple[bytes, bytes]:
        """执行模型推理"""
        try:
            # 预处理
            input_data = self.preprocess_image(image_data)

            # 执行推理
            input_name = self.session.get_inputs()[0].name
            output_name = self.session.get_outputs()[0].name
            mask = self.session.run([output_name], {input_name: input_data})[0]

            # 后处理
            return self.postprocess_mask(mask)

        except Exception as e:
            raise Exception(f"Model inference failed: {str(e)}")


model_service = ModelService()
