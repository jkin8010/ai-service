# AI图片处理服务 (ai-service)

## 项目介绍

此服务是一个统一的AI模型服务管理平台，提供本地模型部署和第三方AI模型接口集成服务。该服务支持模型动态部署、资源调度、负载均衡等功能，并提供了完整的监控和运维体系。

## 主要特性

- 本地模型服务
  - 支持多种AI模型部署
  - 动态资源调度
  - 模型版本管理
  - 性能监控

- 第三方模型集成
  - OpenAI API集成
  - Coze API集成
  - DeepSeek API集成
  - 统一的接口规范

- 分布式计算支持
  - 基于Ray的分布式计算
  - GPU资源池化
  - 动态扩缩容
  - 负载均衡

- 意图识别
  - 用户输入分析
  - 上下文理解
  - 动态路由

## 技术栈

- 后端框架：FastAPI
- 分布式计算：Ray
- 容器化：Docker, Kubernetes
- 数据库：PostgreSQL, Redis
- 对象存储：MinIO
- 监控系统：Prometheus, Grafana
- 日志管理：ELK Stack

## 快速开始

### 环境要求

- Python 3.9+
- CUDA 11.0+ (GPU支持)
- Docker & Docker Compose
- Kubernetes (可选)

### 安装步骤

1. 克隆项目
```bash
git clone https://github.com/jkin8010/ai-service.git
cd ai-service
```

2. 创建虚拟环境
```bash
uv venv
source .venv/bin/activate  # Linux/Mac
# 或
.\.venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
# 或
uv pip install -e .
# 安装开发依赖
uv pip install -e ".[dev]"
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，配置必要的环境变量
```

5. 启动服务
```bash
# 开发环境
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或
uv start

# 生产环境
docker-compose up -d
```

## 项目结构

```
ai-service/
├── app/                    # 应用主目录
│   ├── api/               # API接口
│   ├── core/              # 核心功能
│   ├── models/            # 数据模型
│   └── services/          # 业务服务
├── docs/                  # 文档
│   ├── architecture/      # 架构设计
│   ├── deployment/        # 部署文档
│   └── api-design.md      # API设计
├── tests/                 # 测试用例
├── docker/               # Docker配置
├── kubernetes/           # Kubernetes配置
└── requirements.txt      # 项目依赖
```

## 文档

- [系统架构设计](docs/architecture/system-architecture.md)
- [API接口设计](docs/api-design.md)
- [部署架构设计](docs/deployment.md)
- [Ray部署指南](docs/deployment/ray-deployment-guide.md)

## 开发指南

### 代码规范

- 遵循PEP 8规范
- 使用类型注解
- 编写单元测试
- 添加必要的文档注释

### 提交规范

- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式
- refactor: 重构
- test: 测试相关
- chore: 构建过程或辅助工具的变动

## 部署指南

### Docker部署

```bash
# 构建镜像
docker build -t ai-service .

# 运行容器
docker run -d -p 8000:8000 ai-service
```

### Kubernetes部署

```bash
# 部署服务
kubectl apply -f kubernetes/

# 查看状态
kubectl get pods -l app=ai-service
```

## 监控和运维

### 监控面板

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- Ray Dashboard: http://localhost:8265

### 日志查看

```bash
# 查看服务日志
kubectl logs -f deployment/ai-service

# 查看Ray日志
tail -f /tmp/ray/session_*/logs/ray.log
```

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request
