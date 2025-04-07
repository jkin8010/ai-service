from minio import Minio
from minio.error import S3Error
from app.core.config import settings
import uuid
import os
from typing import Optional, Tuple
import io
from PIL import Image


class MinioClient:
    # 文件类型常量
    FILE_TYPE_ORIGINAL = "original"  # 原始文件
    FILE_TYPE_OUTPUT = "output"  # 处理结果
    FILE_TYPE_MASK = "masks"  # 遮罩文件

    # 支持的图片类型
    SUPPORTED_IMAGE_TYPES = {
        "image/jpeg": [".jpg", ".jpeg"],
        "image/png": [".png"],
        "image/bmp": [".bmp"],
        "image/tiff": [".tiff", ".tif"],
        "image/webp": [".webp"],
    }

    # 限制常量
    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
    MAX_IMAGE_DIMENSION = 3600  # 最大图片尺寸

    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket = settings.MINIO_BUCKET
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """确保存储桶存在"""
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def _validate_file_size(self, file_size: int) -> bool:
        """
        验证文件大小是否在限制范围内

        Args:
            file_size: 文件大小（字节）

        Raises:
            ValueError: 当文件大小超过限制时抛出
        """
        if file_size > self.MAX_FILE_SIZE:
            raise ValueError(
                f"文件大小超过限制: {file_size / 1024 / 1024:.2f}MB，最大支持20MB"
            )
        return True

    def _validate_image_dimensions(self, image_data: bytes) -> bool:
        """
        验证图片尺寸是否在限制范围内

        Args:
            image_data: 图片数据

        Raises:
            ValueError: 当图片尺寸超过限制时抛出
        """
        try:
            # 从字节数据创建图片对象
            image = Image.open(io.BytesIO(image_data))

            # 获取图片尺寸
            width, height = image.size

            # 验证尺寸
            if width > self.MAX_IMAGE_DIMENSION or height > self.MAX_IMAGE_DIMENSION:
                raise ValueError(
                    f"图片尺寸超过限制: {width}x{height}，最大支持{self.MAX_IMAGE_DIMENSION}x{self.MAX_IMAGE_DIMENSION}"
                )

            return True
        except Exception as e:
            raise ValueError(f"无法验证图片尺寸: {str(e)}")

    def _validate_image_type(self, content_type: str, file_name: str) -> bool:
        """
        验证图片类型是否支持

        Args:
            content_type: 文件的MIME类型
            file_name: 文件名

        Returns:
            bool: 是否支持该图片类型

        Raises:
            ValueError: 当图片类型不支持时抛出
        """
        # 获取文件扩展名
        ext = os.path.splitext(file_name)[1].lower()

        # 检查MIME类型是否在支持列表中
        if content_type not in self.SUPPORTED_IMAGE_TYPES:
            raise ValueError(f"不支持的图片类型: {content_type}")

        # 检查文件扩展名是否匹配MIME类型
        if ext not in self.SUPPORTED_IMAGE_TYPES[content_type]:
            raise ValueError(f"文件扩展名 {ext} 与MIME类型 {content_type} 不匹配")

        return True

    def _get_file_name_from_url(self, url: str) -> str:
        """从URL中解析出文件名"""
        # 移除URL参数
        url = url.split("?")[0]
        # 获取最后一个路径部分作为文件名
        return os.path.basename(url)

    def upload_file(self, file_data: bytes, file_url: str, content_type: str) -> str:
        """上传原始文件到MinIO的original目录"""
        try:
            # 从URL中获取原始文件名
            original_name = self._get_file_name_from_url(file_url)

            # 验证文件大小
            self._validate_file_size(len(file_data))

            # 验证图片类型
            self._validate_image_type(content_type, original_name)

            # 验证图片尺寸
            self._validate_image_dimensions(file_data)

            # 生成唯一文件名
            ext = os.path.splitext(original_name)[1]
            unique_name = f"{self.FILE_TYPE_ORIGINAL}/{uuid.uuid4()}{ext}"

            # 将字节数据转换为文件对象
            file_obj = io.BytesIO(file_data)

            # 上传文件到original目录
            self.client.put_object(
                self.bucket,
                unique_name,
                file_obj,
                len(file_data),
                content_type=content_type,
            )

            # 返回文件URL
            return self.client.presigned_get_object(self.bucket, unique_name)
        except S3Error as e:
            raise Exception(f"Failed to upload file: {str(e)}")

    def get_file(self, file_name: str) -> bytes:
        """从MinIO获取文件"""
        try:
            # 处理文件路径，移除重复的bucket前缀
            if file_name.startswith(self.bucket + "/"):
                file_name = file_name[len(self.bucket) + 1 :]
            elif file_name.startswith("/" + self.bucket + "/"):
                file_name = file_name[len("/" + self.bucket) + 1 :]

            # 移除开头的斜杠
            if file_name.startswith("/"):
                file_name = file_name[1:]

            return self.client.get_object(self.bucket, file_name).read()
        except S3Error as e:
            raise Exception(f"Failed to get file: {str(e)}")

    def save_result(
        self, image_data: bytes, mask_data: bytes, task_id: str
    ) -> Tuple[str, str]:
        """保存分割结果和遮罩到指定目录"""
        try:
            # 保存分割结果到 output 目录
            result_name = f"{self.FILE_TYPE_OUTPUT}/{task_id}_result.png"
            self.client.put_object(
                self.bucket, result_name, image_data, len(image_data), "image/png"
            )
            result_url = self.client.presigned_get_object(self.bucket, result_name)

            # 保存遮罩到 masks 目录
            mask_name = f"{self.FILE_TYPE_MASK}/{task_id}_mask.png"
            self.client.put_object(
                self.bucket, mask_name, mask_data, len(mask_data), "image/png"
            )
            mask_url = self.client.presigned_get_object(self.bucket, mask_name)

            return result_url, mask_url
        except S3Error as e:
            raise Exception(f"Failed to save results: {str(e)}")


minio_client = MinioClient()
