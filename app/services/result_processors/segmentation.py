from .base import BaseResultProcessor
from app.utils.minio_client import minio_client
import logging

logger = logging.getLogger(__name__)


class SegmentationResultProcessor(BaseResultProcessor):
    def process(self, result: dict, file_url: str, task_id: str) -> dict:
        result_url, mask_url = minio_client.save_result(
            result["result_image"], result["mask_image"], task_id
        )
        return {
            "segmented_image_url": result_url,
            "mask_image_url": mask_url,
        }
