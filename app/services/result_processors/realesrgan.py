from .base import BaseResultProcessor
from app.utils.minio_client import minio_client
import os
import logging

logger = logging.getLogger(__name__)


class RealESRGANResultProcessor(BaseResultProcessor):
    def process(self, result: dict, file_url: str, task_id: str) -> dict:
        original_file = file_url.split("/")[-1]
        name, ext = os.path.splitext(original_file)
        result_file = f"{name}_upscaled{ext}"

        logger.info(f"Saving upscaled image as {result_file}")
        result_url = minio_client.upload_file(
            result["result_image"], result_file, "image/png"
        )

        return {
            "result_image_url": result_url,
        }
