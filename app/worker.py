import time
from app.utils.redis_client import redis_client
from app.services.task_service import task_service
from app.core.config import settings


def process_tasks():
    """处理任务队列中的任务"""
    while True:
        try:
            # 获取下一个任务
            task_id = redis_client.get_next_task()
            if not task_id:
                time.sleep(1)  # 没有任务时等待
                continue

            # 检查任务是否已在处理中
            if redis_client.is_task_processing(task_id):
                continue

            # 处理任务
            task_service.process_task(task_id)

        except Exception as e:
            print(f"Error processing task: {str(e)}")
            time.sleep(1)  # 发生错误时等待


if __name__ == "__main__":
    process_tasks()
