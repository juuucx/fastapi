from pydantic import BaseModel, Field  # 导入数据模型基类和字段校验工具

class LLMRequest(BaseModel):  # 定义客户端调用模型时提交的请求格式
    prompt: str = Field(min_length=1, max_length=10000)  # 限制提示词长度为 1 到 10000 个字符

class LLMResponse(BaseModel):  # 定义模型调用的响应格式
    answer: str  # 保存模型生成的回答
    model: str  # 保存使用的模型名称
    latency_ms: float  # 保存模型调用耗时，单位为毫秒
    prompt_tokens: int  # 保存输入 Token 数量
    completion_tokens: int  # 保存输出 Token 数量
    total_tokens: int  # 保存总 Token 数量