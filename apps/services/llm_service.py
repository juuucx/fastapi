import os  # 导入 os 模块，用于读取环境变量
import time  # 导入 time 模块，用于计算调用耗时
from dataclasses import dataclass  # 导入 dataclass，用于定义结果对象
from dotenv import load_dotenv  # 导入读取 .env 文件的函数
from openai import OpenAI  # 导入兼容 DeepSeek API 的客户端
from openai import APIConnectionError, APIStatusError, APITimeoutError, APIError  # 导入常见 API 异常类型

load_dotenv()  # 读取 .env 文件中的环境配置

class LLMServiceError(Exception):  # 定义项目自己的模型服务异常
    pass  # 当前不需要增加额外逻辑

@dataclass  # 自动生成初始化等基础方法
class LLMResult:  # 定义模型调用结果的数据结构
    answer: str  # 保存模型回答
    model: str  # 保存模型名称
    latency_ms: float  # 保存调用耗时，单位为毫秒
    prompt_tokens: int  # 保存输入 Token 数量
    completion_tokens: int  # 保存输出 Token 数量
    total_tokens: int  # 保存 Token 总量

def ask_deepseek(user_prompt: str) -> LLMResult:  # 接收用户提示词，返回模型结果对象
    api_key = os.getenv("DEEPSEEK_API_KEY")  # 从环境变量读取 API Key
    if not api_key:  # 检查密钥是否缺失
        raise LLMServiceError("未配置 DEEPSEEK_API_KEY，请检查 .env 文件")  # 缺少密钥时停止调用

    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")  # 读取 API 地址
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-flash")  # 读取模型名称
    client = OpenAI(api_key=api_key, base_url=base_url, timeout=30.0, max_retries=0)  # 创建客户端并设置超时

    start_time = time.perf_counter()  # 在请求前记录开始时间

    try:  # 捕获模型调用过程中可能出现的 API 异常
        response = client.chat.completions.create(  # 向 DeepSeek 发送请求
            model=model,  # 指定使用的模型
            messages=[  # 定义发送给模型的消息列表
                {"role": "system", "content": "你是一个严谨的 AI 质量分析助手，请用清晰准确的中文回答。"},  # 设置模型角色
                {"role": "user", "content": user_prompt},  # 传入用户的问题
            ],  # 消息列表结束
            stream=False,  # 使用非流式响应，一次性获取完整回答
        )  # 完成模型调用

        print(response.model_dump_json(indent=2))  # 将 API 响应对象转换成格式化 JSON 并打印
    except APITimeoutError as exc:  # 捕获请求超时
        raise LLMServiceError("模型请求超时，请稍后重试") from exc  # 转换为项目自己的异常
    except APIConnectionError as exc:  # 捕获网络连接失败
        raise LLMServiceError("无法连接 DeepSeek API，请检查网络") from exc  # 提示网络连接问题
    except APIStatusError as exc:  # 捕获 API 返回的 HTTP 错误状态
        raise LLMServiceError(f"DeepSeek API 请求失败，HTTP 状态码：{exc.status_code}") from exc  # 保留状态码供排查
    except APIError as exc:  # 捕获其他 SDK API 异常
        raise LLMServiceError("模型 API 调用失败，请检查模型配置") from exc  # 转换为统一异常

    latency_ms = (time.perf_counter() - start_time) * 1000  # 计算请求耗时并转换为毫秒
    answer = response.choices[0].message.content  # 提取模型生成的文本
    if not answer:  # 判断模型是否返回空内容
        raise LLMServiceError("模型返回了空回答")  # 空回答时抛出异常

    usage = response.usage  # 获取 API 返回的 Token 用量信息
    prompt_tokens = usage.prompt_tokens if usage else 0  # 获取输入 Token 数，没有用量数据时暂记为 0
    completion_tokens = usage.completion_tokens if usage else 0  # 获取输出 Token 数，没有用量数据时暂记为 0
    total_tokens = usage.total_tokens if usage else 0  # 获取总 Token 数，没有用量数据时暂记为 0

    return LLMResult(  # 创建并返回完整的模型调用结果对象
        answer=answer,  # 保存模型回答
        model=model,  # 保存模型名称
        latency_ms=round(latency_ms, 2),  # 保存耗时并保留两位小数
        prompt_tokens=prompt_tokens,  # 保存输入 Token 数量
        completion_tokens=completion_tokens,  # 保存输出 Token 数量
        total_tokens=total_tokens,  # 保存总 Token 数量
    )  # 返回结果对象