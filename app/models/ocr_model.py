import paddleocr
import numpy as np
from PIL import Image
import io
from typing import Dict
from app.core.model_registry import BaseModel


class OCRModel(BaseModel):
    def __init__(self):
        self.ocr = paddleocr.PaddleOCR(use_angle_cls=True, lang="ch", use_gpu=False)

    def preprocess(self, input_data: bytes) -> bytes:
        """预处理图像"""
        # 读取图像
        image = Image.open(io.BytesIO(input_data))

        # 转换为numpy数组
        image_array = np.array(image)

        # 转换为字节
        buffer = io.BytesIO()
        np.save(buffer, image_array)
        return buffer.getvalue()

    def predict(self, input_data: bytes) -> Dict:
        """执行OCR识别"""
        # 加载预处理数据
        image_array = np.load(io.BytesIO(input_data))

        # 执行OCR
        result = self.ocr.ocr(image_array, cls=True)

        # 后处理
        return self.postprocess(result)

    def postprocess(self, output_data: list) -> Dict:
        """后处理OCR结果"""
        # 提取文本和位置信息
        texts = []
        boxes = []
        scores = []

        for line in output_data:
            for box in line:
                texts.append(box[1][0])  # 文本内容
                boxes.append(box[0])  # 位置坐标
                scores.append(box[1][1])  # 置信度

        return {"texts": texts, "boxes": boxes, "scores": scores}
