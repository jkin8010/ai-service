from .base import BaseResultProcessor
import logging

logger = logging.getLogger(__name__)


class OCRResultProcessor(BaseResultProcessor):
    def process(self, result: dict, file_url: str, task_id: str) -> dict:
        return {
            "texts": result["texts"],
            "boxes": result["boxes"],
            "scores": result["scores"],
        }
