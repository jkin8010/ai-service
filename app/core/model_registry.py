from typing import Dict, Type, Optional
from abc import ABC, abstractmethod
import importlib
import pkg_resources


class BaseModel(ABC):
    """模型基类"""

    @abstractmethod
    def predict(self, input_data: bytes) -> Dict:
        """执行模型推理"""
        pass

    @abstractmethod
    def preprocess(self, input_data: bytes) -> bytes:
        """预处理输入数据"""
        pass

    @abstractmethod
    def postprocess(self, output_data: bytes) -> Dict:
        """后处理输出数据"""
        pass


class ModelRegistry:
    """模型注册中心"""

    def __init__(self):
        self.models: Dict[str, Type[BaseModel]] = {}
        self.model_instances: Dict[str, BaseModel] = {}
        self.model_dependencies: Dict[str, Dict[str, str]] = {}

    def register_model(
        self, model_id: str, model_class: Type[BaseModel], dependencies: Dict[str, str]
    ):
        """注册模型"""
        self.models[model_id] = model_class
        self.model_dependencies[model_id] = dependencies

    def create_model_instance(self, model_id: str) -> BaseModel:
        """创建模型实例"""
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")

        if model_id not in self.model_instances:
            # 检查依赖版本
            self._check_dependencies(model_id)
            # 创建实例
            self.model_instances[model_id] = self.models[model_id]()

        return self.model_instances[model_id]

    def _check_dependencies(self, model_id: str):
        """检查模型依赖版本"""
        dependencies = self.model_dependencies.get(model_id, {})
        for package, version in dependencies.items():
            try:
                pkg_resources.require(f"{package}=={version}")
            except pkg_resources.VersionConflict:
                raise ValueError(f"Version conflict for {package}")
            except pkg_resources.DistributionNotFound:
                raise ValueError(f"Package {package} not found")

    def get_model(self, model_id: str) -> Optional[BaseModel]:
        """获取模型实例"""
        return self.model_instances.get(model_id)

    def list_models(self) -> Dict[str, Dict]:
        """列出所有可用模型"""
        return {
            model_id: {
                "class": model_class.__name__,
                "dependencies": self.model_dependencies.get(model_id, {}),
            }
            for model_id, model_class in self.models.items()
        }


# 创建全局模型注册中心
model_registry = ModelRegistry()
