# Ray集群部署指南

## 1. 环境准备

### 1.1 系统要求
- Python 3.9+
- CUDA 11.0+ (GPU支持，仅Linux/Windows)
- 至少4GB RAM
- 至少20GB磁盘空间

### 1.2 依赖安装
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows

# 安装Ray
pip install "ray[default]"
pip install "ray[tune]"  # 用于超参数调优
pip install "ray[rllib]"  # 用于强化学习
pip install "ray[serve]"  # 用于模型服务
```

## 2. 单机部署

### 2.1 启动Ray集群
```bash
# 启动Ray集群
ray start --head --port=6379 --dashboard-host=0.0.0.0 --dashboard-port=8265

# 启动工作节点
ray start --address='localhost:6379' --redis-password='5241590000000000'
```

### 2.2 验证部署
```python
import ray

# 连接到Ray集群
ray.init(address='localhost:6379', _redis_password='5241590000000000')

# 测试任务
@ray.remote
def hello():
    return "Hello from Ray!"

# 运行任务
future = hello.remote()
result = ray.get(future)
print(result)
```

## 3. 分布式部署

### 3.1 Mac环境下的分布式部署

#### 3.1.1 使用Docker Compose部署（推荐）

```yaml
# docker-compose.yml
version: '3'
services:
  ray-head:
    image: rayproject/ray:latest
    command: ray start --head --port=6379 --dashboard-host=0.0.0.0 --dashboard-port=8265
    ports:
      - "6379:6379"
      - "8265:8265"
    volumes:
      - ./ray:/root/ray
    networks:
      - ray-network
    deploy:
      resources:
        limits:
          cpus: '4'  # 限制CPU使用
          memory: 8G  # 限制内存使用

  ray-worker:
    image: rayproject/ray:latest
    command: ray start --address=ray-head:6379
    depends_on:
      - ray-head
    networks:
      - ray-network
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G

networks:
  ray-network:
    driver: bridge
```

#### 3.1.2 多机器部署（Mac + Mac）

1. 在Mac mini上启动head节点：
```bash
# 在Mac mini上
ray start --head --port=6379 --dashboard-host=0.0.0.0 --dashboard-port=8265
```

2. 在Mac Studio上启动worker节点：
```bash
# 在Mac Studio上
ray start --address='<mac-mini-ip>:6379'
```

3. 配置防火墙：
```bash
# 在Mac mini上
sudo pfctl -f /etc/pf.conf
sudo pfctl -e
```

4. 验证集群状态：
```python
import ray

# 连接到集群
ray.init(address='<mac-mini-ip>:6379')

# 查看集群资源
print(ray.cluster_resources())
```

### 3.2 使用Kubernetes部署

```yaml
# ray-cluster.yaml
apiVersion: ray.io/v1alpha1
kind: RayCluster
metadata:
  name: ray-cluster
spec:
  head:
    serviceType: ClusterIP
    replicas: 1
    rayStartParams:
      dashboard-host: '0.0.0.0'
      num-cpus: '4'
  workers:
    replicas: 3
    rayStartParams:
      num-cpus: '4'
```

## 4. 模型服务部署

### 4.1 使用Ray Serve部署模型

```python
from ray import serve
from ray.serve.drivers import DefaultgRPCDriver

# 定义模型服务
@serve.deployment
class ModelService:
    def __init__(self):
        self.model = load_model()  # 加载模型

    async def __call__(self, request):
        return self.model.predict(request)

# 部署服务
serve.start()
ModelService.options(name="model_service").deploy()
```

### 4.2 配置模型服务

```yaml
# model-service-config.yaml
apiVersion: ray.io/v1alpha1
kind: RayService
metadata:
  name: model-service
spec:
  serveConfigV2:
    applications:
      - name: model_service
        import_path: model_service:ModelService
        runtime_env:
          working_dir: "."
          pip: ["torch", "transformers"]
```

## 5. 监控和管理

### 5.1 访问Ray Dashboard
- URL: http://localhost:8265
- 功能：
  - 集群状态监控
  - 任务追踪
  - 资源使用统计
  - 性能分析

### 5.2 常用管理命令
```bash
# 查看集群状态
ray status

# 停止集群
ray stop

# 查看任务状态
ray timeline

# 查看资源使用
ray memory
```

## 6. 故障排除

### 6.1 常见问题
1. 连接问题
   - 检查网络连接
   - 验证端口是否开放
   - 确认防火墙设置
   - Mac环境特别检查：
     - 防火墙设置
     - 网络共享设置
     - 端口转发配置

2. 资源问题
   - 检查内存使用
   - 验证CPU可用性
   - 监控磁盘空间
   - Mac环境特别检查：
     - CPU使用率
     - 内存压力
     - 散热情况

3. 性能问题
   - 使用Ray Timeline分析
   - 检查任务调度
   - 优化资源分配
   - Mac环境优化：
     - 调整CPU核心数
     - 优化内存分配
     - 使用SSD存储

### 6.2 日志查看
```bash
# 查看Ray日志
tail -f /tmp/ray/session_*/logs/ray.log

# 查看特定任务日志
ray timeline
```

## 7. 最佳实践

### 7.1 资源管理
- 合理设置CPU资源
- 使用资源限制
- 实现动态扩缩容
- Mac环境特别建议：
  - 预留系统资源
  - 监控温度
  - 避免过度使用

### 7.2 性能优化
- 使用对象存储
- 优化数据传输
- 实现任务批处理
- Mac环境优化：
  - 使用本地存储
  - 优化网络传输
  - 合理设置批处理大小

### 7.3 安全配置
- 设置访问密码
- 配置SSL/TLS
- 实现访问控制
- Mac环境安全：
  - 配置防火墙规则
  - 使用VPN（如需要）
  - 定期更新系统 