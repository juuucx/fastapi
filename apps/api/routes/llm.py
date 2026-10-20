from fastapi import APIRouter, HTTPException  # 导入路由类和 HTTP 异常类
from apps.schemas.llm import LLMRequest, LLMResponse  # 导入请求和响应数据模型
from apps.services.llm_service import ask_deepseek, LLMServiceError  # 导入模型调用函数和自定义异常

router = APIRouter(prefix="/llm", tags=["LLM"])  # 创建路由，并为接口统一添加 /llm 前缀

@router.post("/chat", response_model=LLMResponse)  # 注册 POST /llm/chat 接口，并规定响应格式
def chat_with_llm(data: LLMRequest):  # 接收经过校验的请求对象
    try:  # 开始处理模型服务调用
        result = ask_deepseek(data.prompt)  # 调用模型并获取完整结果对象
        return LLMResponse(  # 将服务结果转换为 API 响应模型
            answer=result.answer,  # 返回模型生成的文本
            model=result.model,  # 返回模型名称
            latency_ms=result.latency_ms,  # 返回请求耗时
            prompt_tokens=result.prompt_tokens,  # 返回输入 Token 数
            completion_tokens=result.completion_tokens,  # 返回输出 Token 数
            total_tokens=result.total_tokens,  # 返回 Token 总数
        )  # 完成响应对象构建
    except LLMServiceError as exc:  # 捕获模型服务层的统一异常
        raise HTTPException(status_code=502, detail=str(exc)) from exc  # 将上游调用失败转换为 HTTP 502