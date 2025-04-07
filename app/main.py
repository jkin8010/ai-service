from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import tasks, matting, upscale

app = FastAPI(title="AI Service", description="AI模型服务API", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(matting.router, prefix="/api/v1/matting", tags=["matting"])
app.include_router(upscale.router, prefix="/api/v1/upscale", tags=["upscale"])


@app.get("/")
async def root():
    return {"message": "Welcome to AI Service"}


@app.get("/health")
async def health():
    return {"status": "ok"}
