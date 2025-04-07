from app.core.model_registry import model_registry
from app.models.birefnet_model import BiRefNetModel
from app.models.realesrgan_model import RealESRGANModel

# 共享的依赖配置
BIREFNET_DEPS = {
    "torch": "2.5.1",
    "torchvision": "0.20.1",
    "numpy": "1.26.4",
    "Pillow": "11.1.0",
    "opencv-python": "4.11.0.86",
    "timm": "1.0.15",
    "scipy": "1.15.2",
    "scikit-image": "0.25.2",
    "kornia": "0.8.0",
    "einops": "0.8.1",
    "transformers": "4.49.0",
    "huggingface-hub": "0.29.3",
    "accelerate": "1.5.2",
}

# 注册所有BiRefNet模型变体
model_registry.register_model(
    "birefnet",
    BiRefNetModel,
    BIREFNET_DEPS,
)

model_registry.register_model(
    "birefnet-hr",
    BiRefNetModel,
    BIREFNET_DEPS,
)

model_registry.register_model(
    "birefnet-portrait",
    BiRefNetModel,
    BIREFNET_DEPS,
)

# RealESRGAN模型依赖配置
REALESRGAN_DEPS = {
    "torch": "2.5.1",
    "torchvision": "0.20.1",
    "numpy": "1.26.4",
    "Pillow": "11.1.0",
    "opencv-python": "4.11.0.86",
    "huggingface-hub": "0.29.3",
}

# 注册RealESRGAN模型
model_registry.register_model(
    "realesrgan",
    RealESRGANModel,
    REALESRGAN_DEPS,
)
