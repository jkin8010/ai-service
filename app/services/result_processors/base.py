from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class BaseResultProcessor(ABC):
    """结果处理器基类"""

    @abstractmethod
    def process(
        self, result: Dict[str, Any], file_url: str, task_id: str
    ) -> Dict[str, Any]:
        """处理模型结果"""
        pass
