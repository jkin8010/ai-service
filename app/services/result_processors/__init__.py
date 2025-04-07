from typing import Dict, Type
from .base import BaseResultProcessor
from .segmentation import SegmentationResultProcessor
from .ocr import OCRResultProcessor
from .realesrgan import RealESRGANResultProcessor


class ResultProcessorFactory:
    _processors: Dict[str, Type[BaseResultProcessor]] = {
        "segmentation": SegmentationResultProcessor,
        "ocr": OCRResultProcessor,
        "realesrgan": RealESRGANResultProcessor,
    }

    @classmethod
    def get_processor(cls, model_id: str) -> BaseResultProcessor:
        processor_class = cls._processors.get(model_id)
        if not processor_class:
            raise ValueError(f"No processor found for model: {model_id}")
        return processor_class()
