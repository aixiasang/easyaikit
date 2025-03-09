"""
EasyOpenAI 客户端 - 提供对 OpenAI API 的简单封装
"""

import os
from typing import Optional, Dict, List, Any, Generator, Union, Tuple

from openai import OpenAI

from easyopenai.session import ChatSession
from easyopenai.storage import DBStorage, JSONStorage


class AI:
    """
    OpenAI API 的简单封装
    
    提供了便捷的接口来使用 OpenAI 的 API，简化了常见操作，比如发送问题、
    流式接收回复等。
    
    示例:
        ```python
        # 基本用法
        client = AI()
        response = client.ask("什么是机器学习？")
        print(response)
        
        # 流式输出
        for chunk in client.stream_ask("简单介绍一下Python"):
            print(chunk, end="")
        
        # 使用会话接口
        session = client.session()
        response = session.ask("什么是神经网络？")
        print(response)
        response = session.ask("它们有什么实际应用？")
        print(response)
        ```
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
        system_message: str = "你是人工智能助手",
        timeout: Optional[float] = None,
        max_retries: int = 2,
    ):
        """
        初始化 EasyOpenAI 封装
        
        参数:
            api_key: OpenAI API 密钥。如果为 None，将从环境变量 ARK_API_KEY 获取
            base_url: API 基础 URL。如果为 None，将使用默认值
            default_model: 默认使用的模型
            system_message: 默认的系统消息
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        # 配置默认值
        self.api_key = api_key or os.environ.get("ARK_API_KEY")
        if not self.api_key:
            raise ValueError("API 密钥必须通过参数或环境变量 ARK_API_KEY 提供")
        
        self.base_url = base_url or "https://ark.cn-beijing.volces.com/api/v3"
        self.default_model = default_model or "deepseek-r1-distill-qwen-32b-250120"
        self.default_system_message = system_message
        
        # 初始化 OpenAI 客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=timeout,
            max_retries=max_retries
        )
    
    def ask(
        self,
        question: str,
        messages: Optional[List[Dict[str, str]]] = None,
        system_message: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        向 AI 发送问题并获取回答
        
        参数:
            question: 要询问的问题
            messages: 历史消息列表，用于多轮对话
            system_message: 系统消息，用于指导 AI 的行为
            model: 要使用的模型
            temperature: 生成的随机性，0-1 之间的值
            max_tokens: 生成的最大标记数
            **kwargs: 传递给 OpenAI API 的其他参数
        
        返回:
            AI 的回答文本
        """
        # 准备消息
        if messages:
            # 如果提供了历史消息，使用它们
            current_messages = messages.copy()
            # 添加当前问题
            current_messages.append({"role": "user", "content": question})
        else:
            # 否则创建新的消息列表
            current_messages = [
                {"role": "system", "content": system_message or self.default_system_message},
                {"role": "user", "content": question}
            ]
        
        # 准备创建参数
        create_params = {
            "model": model or self.default_model,
            "messages": current_messages,
        }
        
        # 添加可选参数
        if temperature is not None:
            create_params["temperature"] = temperature
        if max_tokens is not None:
            create_params["max_tokens"] = max_tokens
            
        # 添加其他参数
        create_params.update(kwargs)
        
        # 发送请求
        response = self.client.chat.completions.create(**create_params)
        
        # 返回回答文本
        return response.choices[0].message.content
    
    def stream_ask(
        self,
        question: str,
        messages: Optional[List[Dict[str, str]]] = None,
        system_message: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """
        向 AI 发送问题并流式获取回答
        
        参数:
            question: 要询问的问题
            messages: 历史消息列表，用于多轮对话
            system_message: 系统消息，用于指导 AI 的行为
            model: 要使用的模型
            temperature: 生成的随机性，0-1 之间的值
            max_tokens: 生成的最大标记数
            **kwargs: 传递给 OpenAI API 的其他参数
            
        返回:
            产生回答文本块的生成器
        """
        # 准备消息
        if messages:
            # 如果提供了历史消息，使用它们
            current_messages = messages.copy()
            # 添加当前问题
            current_messages.append({"role": "user", "content": question})
        else:
            # 否则创建新的消息列表
            current_messages = [
                {"role": "system", "content": system_message or self.default_system_message},
                {"role": "user", "content": question}
            ]
        
        # 准备创建参数
        create_params = {
            "model": model or self.default_model,
            "messages": current_messages,
            "stream": True,
        }
        
        # 添加可选参数
        if temperature is not None:
            create_params["temperature"] = temperature
        if max_tokens is not None:
            create_params["max_tokens"] = max_tokens
            
        # 添加其他参数
        create_params.update(kwargs)
        
        # 发送请求
        response_stream = self.client.chat.completions.create(**create_params)
        
        # 逐块产生回答
        for chunk in response_stream:
            if not chunk.choices:
                continue
            content = chunk.choices[0].delta.content
            if content:
                yield content
    
    def session(
        self, 
        system_message: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> "ChatSession":
        """
        创建一个新的聊天会话
        
        会话可以保持对话历史，便于进行多轮对话。
        
        参数:
            system_message: 会话的系统消息
            model: 会话使用的默认模型
            api_key: OpenAI API 密钥
            base_url: API 基础 URL
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            temperature: 生成的随机性，0-1 之间的值
            max_tokens: 生成的最大标记数
            **kwargs: 其他参数传递给 ChatSession
            
        返回:
            ChatSession 实例
        """
        # 如果用户提供了新的 API 配置，创建新的客户端
        if api_key or base_url or timeout is not None or max_retries is not None:
            new_client = AI(
                api_key=api_key or self.api_key,
                base_url=base_url or self.base_url,
                default_model=model or self.default_model,
                system_message=system_message or self.default_system_message,
                timeout=timeout if timeout is not None else self.client._timeout,
                max_retries=max_retries if max_retries is not None else self.client._max_retries
            )
            client = new_client
        else:
            client = self

        # 准备会话参数
        session_kwargs = {}
        if temperature is not None:
            session_kwargs["temperature"] = temperature
        if max_tokens is not None:
            session_kwargs["max_tokens"] = max_tokens
        session_kwargs.update(kwargs)
        
        return ChatSession(
            client=client,
            system_message=system_message or self.default_system_message,
            model=model or self.default_model,
            **session_kwargs
        )
    
    def get_openai_client(self) -> OpenAI:
        """
        获取底层的 OpenAI 客户端实例
        
        返回:
            OpenAI 客户端实例
        """
        return self.client
    
    def load_db(
        self,
        db_path: str,
        db_type: str = "sqlite",
        table_prefix: str = "ai_message",
        session_id: Optional[str] = None
    ) -> "DBStorage":
        """
        加载数据库存储
        
        参数:
            db_path: 数据库路径
            db_type: 数据库类型，目前支持 sqlite
            table_prefix: 表名前缀
            session_id: 指定的会话ID
            
        返回:
            DBStorage 实例
        """
        from easyopenai.storage import DBStorage
        return DBStorage(
            db_path=db_path,
            db_type=db_type,
            table_prefix=table_prefix,
            session_id=session_id
        )
    
    def load_json(
        self,
        file_path: str,
        session_id: Optional[str] = None
    ) -> "JSONStorage":
        """
        加载 JSON 文件存储
        
        参数:
            file_path: JSON 文件路径
            session_id: 指定的会话ID
            
        返回:
            JSONStorage 实例
        """
        from easyopenai.storage import JSONStorage
        return JSONStorage(
            file_path=file_path,
            session_id=session_id
        )

    def think(
        self,
        question: str,
        messages: Optional[List[Dict[str, str]]] = None,
        system_message: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Tuple[str, str]:
        """
        向 AI 发送问题并获取思考过程和回答
        
        参数:
            question: 要询问的问题
            messages: 历史消息列表，用于多轮对话
            system_message: 系统消息，用于指导 AI 的行为
            model: 要使用的模型
            temperature: 生成的随机性，0-1 之间的值
            max_tokens: 生成的最大标记数
            **kwargs: 传递给 OpenAI API 的其他参数
            
        返回:
            (思考过程, 最终回答) 的元组
        """
        # 准备消息
        if messages:
            # 如果提供了历史消息，使用它们
            current_messages = messages.copy()
            # 添加当前问题
            current_messages.append({"role": "user", "content": question})
        else:
            # 否则创建新的消息列表
            current_messages = [
                {"role": "system", "content": system_message or self.default_system_message},
                {"role": "user", "content": question}
            ]
        
        # 准备创建参数
        create_params = {
            "model": model or self.default_model,
            "messages": current_messages,
            "stream": True,  # 使用流式响应来分离思考过程和回答
        }
        
        # 添加可选参数
        if temperature is not None:
            create_params["temperature"] = temperature
        if max_tokens is not None:
            create_params["max_tokens"] = max_tokens
            
        # 添加其他参数
        create_params.update(kwargs)
        
        # 发送请求
        response = self.client.chat.completions.create(**create_params)
        
        # 收集思考过程和回答
        reasoning_content = ""
        answer_content = ""
        is_answering = False
        
        for chunk in response:
            if not chunk.choices:
                continue
            
            delta = chunk.choices[0].delta
            
            # 处理思考过程
            if hasattr(delta, 'reasoning_content') and delta.reasoning_content is not None:
                reasoning_content += delta.reasoning_content
            else:
                # 处理回答
                if delta.content:
                    answer_content += delta.content
                    is_answering = True
        
        return reasoning_content.strip(), answer_content.strip()
    
    def stream_think(
        self,
        question: str,
        messages: Optional[List[Dict[str, str]]] = None,
        system_message: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Generator[Union[Tuple[str, None], Tuple[None, str]], None, None]:
        """
        向 AI 发送问题并流式获取思考过程和回答
        
        参数:
            参数与 think 方法相同
            
        返回:
            生成器，产生 (思考内容, None) 或 (None, 回答内容) 的元组
        """
        # 准备消息
        if messages:
            current_messages = messages.copy()
            current_messages.append({"role": "user", "content": question})
        else:
            current_messages = [
                {"role": "system", "content": system_message or self.default_system_message},
                {"role": "user", "content": question}
            ]
        
        # 准备创建参数
        create_params = {
            "model": model or self.default_model,
            "messages": current_messages,
            "stream": True,
        }
        
        if temperature is not None:
            create_params["temperature"] = temperature
        if max_tokens is not None:
            create_params["max_tokens"] = max_tokens
            
        create_params.update(kwargs)
        
        # 发送请求
        response = self.client.chat.completions.create(**create_params)
        
        # 流式返回思考过程和回答
        for chunk in response:
            if not chunk.choices:
                continue
            
            delta = chunk.choices[0].delta
            
            # 返回思考过程
            if hasattr(delta, 'reasoning_content') and delta.reasoning_content is not None:
                yield delta.reasoning_content, None
            # 返回回答
            elif delta.content:
                yield None, delta.content

    def ask_json(
        self,
        question: str,
        messages: Optional[List[Dict[str, str]]] = None,
        system_message: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        向 AI 发送问题并获取 JSON 格式的回答
        
        参数:
            question: 要询问的问题
            messages: 历史消息列表，用于多轮对话
            system_message: 系统消息，用于指导 AI 的行为
            model: 要使用的模型
            temperature: 生成的随机性，0-1 之间的值
            max_tokens: 生成的最大标记数
            **kwargs: 传递给 OpenAI API 的其他参数
            
        返回:
            JSON 格式的回答
        """
        # 准备系统消息，强调返回 JSON 格式
        json_system_message = (
            "你是一个专门输出 JSON 格式的助手。"
            "你的回答必须是一个有效的 JSON 对象，不要包含任何其他文本。"
            "不要使用 Markdown 代码块。"
            "确保所有的键名使用双引号，避免使用单引号。"
            "如果需要解释或描述，请将其作为 JSON 对象中的一个字段。"
        )
        
        if system_message:
            json_system_message = f"{json_system_message} {system_message}"
        
        # 修改问题以强调 JSON 格式
        json_question = f"请以纯JSON格式回答以下问题（不要使用Markdown代码块，直接返回JSON）：{question}"
        
        # 准备消息
        if messages:
            current_messages = messages.copy()
            current_messages.append({"role": "user", "content": json_question})
        else:
            current_messages = [
                {"role": "system", "content": json_system_message},
                {"role": "user", "content": json_question}
            ]
        
        # 准备创建参数
        create_params = {
            "model": model or self.default_model,
            "messages": current_messages,
            "response_format": {"type": "json_object"},  # 指定返回 JSON 格式
        }
        
        # 添加可选参数
        if temperature is not None:
            create_params["temperature"] = temperature
        if max_tokens is not None:
            create_params["max_tokens"] = max_tokens
            
        # 添加其他参数
        create_params.update(kwargs)
        
        # 发送请求
        response = self.client.chat.completions.create(**create_params)
        content = response.choices[0].message.content
        
        try:
            # 清理响应内容
            import re
            # 移除可能的 Markdown 代码块
            content = re.sub(r'```(?:json)?\n?(.*?)\n?```', r'\1', content, flags=re.DOTALL)
            # 移除开头和结尾的空白字符
            content = content.strip()
            
            # 尝试解析 JSON 响应
            import json
            return json.loads(content)
        except json.JSONDecodeError as e:
            # 如果解析失败，返回错误信息的 JSON 对象
            return {
                "error": "Invalid JSON response",
                "message": str(e),
                "raw_response": content
            }


# 便捷函数，无需创建客户端实例即可使用
def ask(
    question: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    system_message: Optional[str] = None,
    **kwargs
) -> str:
    """
    向 AI 发送问题并获取回答（便捷函数）
    
    参数:
        question: 要询问的问题
        api_key: OpenAI API 密钥
        model: 要使用的模型
        system_message: 系统消息
        **kwargs: 其他参数传递给 EasyOpenAI.ask
        
    返回:
        AI 的回答文本
    """
    client = AI(api_key=api_key)
    return client.ask(
        question=question,
        model=model,
        system_message=system_message,
        **kwargs
    )


def stream_ask(
    question: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    system_message: Optional[str] = None,
    **kwargs
) -> Generator[str, None, None]:
    """
    向 AI 发送问题并流式获取回答（便捷函数）
    
    参数:
        question: 要询问的问题
        api_key: OpenAI API 密钥
        model: 要使用的模型
        system_message: 系统消息
        **kwargs: 其他参数传递给 EasyOpenAI.stream_ask
        
    返回:
        产生回答文本块的生成器
    """
    client = AI(api_key=api_key)
    return client.stream_ask(
        question=question,
        model=model,
        system_message=system_message,
        **kwargs
    ) 