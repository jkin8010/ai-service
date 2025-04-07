# AI服务API接口设计

## 1. API概述

### 1.1 基础信息
- 基础路径: `/api/v1/ai`
- 认证方式: Bearer Token
- 响应格式: JSON
- 编码方式: UTF-8

### 1.2 通用响应格式

```json
{
    "code": 0,           // 状态码，0表示成功
    "message": "success", // 状态信息
    "data": {            // 响应数据
        // 具体数据字段
    }
}
```

### 1.3 错误码说明

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1001 | 参数错误 |
| 1002 | 认证失败 |
| 1003 | 权限不足 |
| 2001 | 模型服务异常 |
| 2002 | 资源不足 |
| 3001 | 第三方服务异常 |

## 2. 本地模型API

### 2.1 模型列表

#### 请求信息
- 路径: `/api/v1/ai/models`
- 方法: GET
- 描述: 获取可用的本地模型列表

#### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| size | integer | 否 | 每页数量，默认20 |

#### 响应示例
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "total": 100,
        "items": [
            {
                "model_id": "model_001",
                "name": "文本分类模型",
                "version": "1.0.0",
                "status": "running",
                "resource_usage": {
                    "gpu_memory": "4GB",
                    "cpu_usage": "30%"
                }
            }
        ]
    }
}
```

### 2.2 模型推理

#### 请求信息
- 路径: `/api/v1/ai/models/{model_id}/inference`
- 方法: POST
- 描述: 调用指定模型进行推理

#### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| model_id | string | 是 | 模型ID |
| input_data | object | 是 | 输入数据 |
| options | object | 否 | 推理选项 |

#### 响应示例
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "result": {
            // 模型推理结果
        },
        "metadata": {
            "inference_time": 0.5,
            "model_version": "1.0.0"
        }
    }
}
```

## 3. 第三方模型API

### 3.1 Coze模型调用

#### 请求信息
- 路径: `/api/v1/ai/third-party/coze`
- 方法: POST
- 描述: 调用Coze模型服务

#### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| bot_id | string | 是 | Coze机器人ID |
| message | string | 是 | 输入消息 |
| conversation_id | string | 否 | 会话ID |

#### 响应示例
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "response": "模型回复内容",
        "conversation_id": "会话ID"
    }
}
```

### 3.2 OpenAI模型调用

#### 请求信息
- 路径: `/api/v1/ai/third-party/openai`
- 方法: POST
- 描述: 调用OpenAI模型服务

#### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| model | string | 是 | 模型名称 |
| messages | array | 是 | 消息列表 |
| temperature | float | 否 | 温度参数 |

#### 响应示例
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "choices": [
            {
                "message": {
                    "content": "模型回复内容",
                    "role": "assistant"
                }
            }
        ]
    }
}
```

## 4. 意图识别API

### 4.1 意图分析

#### 请求信息
- 路径: `/api/v1/ai/intent/analyze`
- 方法: POST
- 描述: 分析用户输入意图

#### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| text | string | 是 | 用户输入文本 |
| context | object | 否 | 上下文信息 |

#### 响应示例
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "intent": "image_generation",
        "confidence": 0.95,
        "entities": [
            {
                "type": "style",
                "value": "realistic"
            }
        ]
    }
}
```

## 5. 模型管理API

### 5.1 模型部署

#### 请求信息
- 路径: `/api/v1/ai/models/deploy`
- 方法: POST
- 描述: 部署新模型

#### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| model_config | object | 是 | 模型配置 |
| resources | object | 是 | 资源需求 |

#### 响应示例
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "deployment_id": "deploy_001",
        "status": "deploying"
    }
}
```

### 5.2 模型状态查询

#### 请求信息
- 路径: `/api/v1/ai/models/{model_id}/status`
- 方法: GET
- 描述: 查询模型部署状态

#### 响应示例
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "status": "running",
        "health": "healthy",
        "metrics": {
            "requests_per_second": 10,
            "average_latency": 0.2
        }
    }
}
``` 