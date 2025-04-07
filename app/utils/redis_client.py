import redis
import json
from datetime import datetime, UTC
from typing import Optional, Dict, Any
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class RedisClient:
    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )

    def create_task(self, task_id: str, file_url: str, model_id: str) -> Dict[str, Any]:
        """创建新任务"""
        task_data = {
            "task_id": str(task_id),
            "file_url": str(file_url),
            "model_id": str(model_id),
            "status": "pending",
            "created_at": datetime.now(UTC).isoformat(),
            "error": "",
            "result": "",
        }

        # 保存任务数据
        self.client.hmset(f"task:{task_id}", task_data)

        # 添加到任务队列
        self.client.lpush("task_queue", task_id)

        return task_data

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务信息"""
        task_data = self.client.hgetall(f"task:{task_id}")
        if not task_data:
            return None

        # 解析result字段的JSON字符串
        if task_data.get("result"):
            try:
                task_data["result"] = json.loads(task_data["result"])
            except json.JSONDecodeError:
                # 如果解析失败，保持原样
                pass

        return task_data

    def update_task_status(
        self,
        task_id: str,
        status: str,
        error: Optional[str] = None,
        result: Optional[Dict] = None,
    ):
        """更新任务状态"""
        update_data = {
            "status": str(status),
            "error": str(error) if error is not None else "",
            "completed_at": (
                datetime.now(UTC).isoformat()
                if status in ["completed", "failed"]
                else ""
            ),
        }

        if result:
            # 确保结果中的所有值都是字符串类型
            update_data["result"] = json.dumps(result)

        self.client.hmset(f"task:{task_id}", update_data)

    def get_next_task(self) -> Optional[str]:
        """获取下一个待处理任务"""
        return self.client.rpop("task_queue")

    def is_task_processing(self, task_id: str) -> bool:
        """检查任务是否正在处理中"""
        return self.client.sismember("processing_tasks", task_id)

    def mark_task_processing(self, task_id: str):
        """标记任务为处理中"""
        self.client.sadd("processing_tasks", task_id)
        self.update_task_status(task_id, "processing")

    def mark_task_completed(self, task_id: str, result: Dict):
        """标记任务为完成"""
        self.client.srem("processing_tasks", task_id)
        self.update_task_status(task_id, "completed", result=result)

    def mark_task_failed(self, task_id: str, error: str):
        """标记任务为失败"""
        self.client.srem("processing_tasks", task_id)
        self.update_task_status(task_id, "failed", error=error)

    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        try:
            key = f"task:{task_id}"
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Failed to delete task {task_id}: {str(e)}")
            return False


redis_client = RedisClient()
