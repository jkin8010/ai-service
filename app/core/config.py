from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # MinIO配置
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "ai-segmentation"
    MINIO_SECURE: bool = False

    # 模型配置
    MODEL_PATH: str = "models/segmentation.onnx"
    MODEL_INPUT_SIZE: List[int] = [256, 256]

    # 任务配置
    TASK_TIMEOUT: int = 300  # 秒
    TASK_POLL_INTERVAL: int = 2  # 秒
    TASK_MAX_POLLS: int = 150  # 最大轮询次数

    class Config:
        env_file = ".env"


settings = Settings()
