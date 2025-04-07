import uuid
from typing import Dict, Any, Optional
import base64
from app.utils.minio_client import minio_client
from app.utils.redis_client import redis_client
from app.core.model_registry import model_registry
from app.services.result_processors import ResultProcessorFactory
import os
from PIL import Image
import io
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, Future

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskService:
    def __init__(self):
        self.running_tasks = {}  # 存储正在运行的任务
        self.executor = ThreadPoolExecutor(max_workers=4)  # 控制并发任务数
        self._lock = threading.Lock()  # 线程锁

    def create_task(self, task_id: str, file_url: str, model_id: str) -> Dict[str, Any]:
        """创建新任务"""
        try:
            # 检查模型是否存在
            if model_id not in model_registry.models:
                raise ValueError(f"Model {model_id} not found")

            # 创建任务记录
            task_data = redis_client.create_task(task_id, file_url, model_id)
            logger.info(f"Created task: {task_id} for model: {model_id}")

            return task_data

        except Exception as e:
            logger.error(f"Failed to create task: {str(e)}")
            raise Exception(f"Failed to create task: {str(e)}")

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        return redis_client.get_task(task_id)

    async def delete_task(self, task_id: str) -> bool:
        """删除任务并停止处理"""
        try:
            # 获取任务信息
            task_data = redis_client.get_task(task_id)
            if not task_data:
                return False

            # 如果任务正在运行，停止它
            with self._lock:
                if task_id in self.running_tasks:
                    logger.info(f"Stopping running task: {task_id}")
                    # 取消任务
                    future = self.running_tasks[task_id]
                    future.cancel()
                    # 从运行任务列表中移除
                    del self.running_tasks[task_id]

            # 从Redis中删除任务
            redis_client.delete_task(task_id)
            logger.info(f"Task {task_id} deleted successfully")

            return True
        except Exception as e:
            logger.error(f"Failed to delete task {task_id}: {str(e)}")
            return False

    def process_task(self, task_id: str):
        """处理任务"""
        future = None
        try:
            logger.info(f"Starting to process task: {task_id}")

            # 获取任务信息
            task_data = redis_client.get_task(task_id)
            if not task_data:
                logger.error(f"Task not found: {task_id}")
                raise Exception("Task not found")

            # 标记任务为处理中
            redis_client.mark_task_processing(task_id)
            logger.info(f"Task {task_id} marked as processing")

            # 获取模型实例
            model_id = task_data["model_id"]
            logger.info(f"Creating model instance for {model_id}")
            model = model_registry.create_model_instance(model_id)

            # 下载图片
            file_url = task_data["file_url"]
            logger.info(f"Downloading image from {file_url}")
            image_data = minio_client.get_file(file_url)

            # 创建一个Future对象来跟踪任务
            with self._lock:
                future = Future()
                self.running_tasks[task_id] = future

            try:
                # 检查任务是否已被取消
                if future.cancelled():
                    logger.info(f"Task {task_id} was cancelled before processing")
                    redis_client.mark_task_failed(task_id, "Task was cancelled")
                    return

                # 执行模型推理
                logger.info(f"Running model inference for task {task_id}")
                result = model.predict(image_data)

                # 检查任务是否在处理过程中被取消
                if future.cancelled():
                    logger.info(f"Task {task_id} was cancelled during processing")
                    redis_client.mark_task_failed(task_id, "Task was cancelled")
                    return

                # 获取对应的结果处理器
                processor = ResultProcessorFactory.get_processor(model_id)
                result_data = processor.process(result, file_url, task_id)

                # 再次检查任务是否被取消
                if future and not future.cancelled():
                    # 更新任务状态
                    logger.info(f"Task {task_id} completed successfully")
                    redis_client.mark_task_completed(task_id, result_data)
                    future.set_result(result_data)
                else:
                    logger.info(f"Task {task_id} was cancelled before completion")
                    redis_client.mark_task_failed(task_id, "Task was cancelled")

            except Exception as e:
                logger.error(f"Task {task_id} failed with error: {str(e)}")
                redis_client.mark_task_failed(task_id, str(e))
                if future and not future.cancelled():
                    future.set_exception(e)
                raise

            finally:
                # 从运行任务列表中移除
                with self._lock:
                    if task_id in self.running_tasks:
                        del self.running_tasks[task_id]

        except Exception as e:
            logger.error(f"Task {task_id} failed with error: {str(e)}")
            redis_client.mark_task_failed(task_id, str(e))
            raise


task_service = TaskService()
