# FastAPI 工程笔记

FastAPI 基于 ASGI，使用 Pydantic 进行请求校验，并自动生成 OpenAPI/Swagger 文档。依赖注入适合管理数据库连接、认证和服务对象。上传文件应校验扩展名、大小和安全文件名，避免路径穿越。

生产部署通常使用 uvicorn worker 或 gunicorn，并通过结构化日志记录 request_id、耗时、异常和下游调用状态。敏感配置应从环境变量读取。
