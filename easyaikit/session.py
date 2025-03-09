"""
EasyOpenAI 会话模块 - 提供对话会话功能
"""

from typing import List, Dict, Any, Optional, Generator, Tuple, Union


class ChatSession:
    """
    聊天会话类
    
    维护对话历史，便于进行多轮对话。
    
    示例:
        ```python
        client = EasyOpenAI()
        session = client.session()
        
        # 第一轮对话
        response = session.ask("什么是机器学习？")
        print(response)
        
        # 第二轮对话（历史会自动保存）
        response = session.ask("它与深度学习有什么区别？")
        print(response)
        ```
    """
    
    def __init__(
        self,
        client,
        system_message: str = "你是人工智能助手",
        model: Optional[str] = None
    ):
        """
        初始化聊天会话
        
        参数:
            client: EasyOpenAI 客户端实例
            system_message: 会话的系统消息
            model: 会话使用的默认模型
        """
        self.client = client
        self.system_message = system_message
        self.model = model
        
        # 初始化会话历史
        self.history = []
        self.messages = [
            {"role": "system", "content": system_message}
        ]
    
    def ask(
        self,
        question: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        向会话发送问题并获取回答
        
        参数:
            question: 要询问的问题
            model: 要使用的模型（覆盖会话默认模型）
            temperature: 生成的随机性，0-1 之间的值
            max_tokens: 生成的最大标记数
            **kwargs: 传递给 OpenAI API 的其他参数
            
        返回:
            AI 的回答文本
        """
        # 添加用户问题到消息列表
        self.messages.append({"role": "user", "content": question})
        
        # 准备创建参数
        create_params = {
            "model": model or self.model or self.client.default_model,
            "messages": self.messages.copy(),
        }
        
        # 添加可选参数
        if temperature is not None:
            create_params["temperature"] = temperature
        if max_tokens is not None:
            create_params["max_tokens"] = max_tokens
            
        # 添加其他参数
        create_params.update(kwargs)
        
        # 发送请求
        response = self.client.client.chat.completions.create(**create_params)
        
        # 获取回答
        answer = response.choices[0].message.content
        
        # 将回答添加到消息列表
        self.messages.append({"role": "assistant", "content": answer})
        
        # 同时更新历史记录（不包含系统消息）
        if len(self.messages) > 1:
            self.history = self.messages[1:]
        
        return answer
    
    def stream_ask(
        self,
        question: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """
        向会话发送问题并流式获取回答
        
        参数:
            question: 要询问的问题
            model: 要使用的模型（覆盖会话默认模型）
            temperature: 生成的随机性，0-1 之间的值
            max_tokens: 生成的最大标记数
            **kwargs: 传递给 OpenAI API 的其他参数
            
        返回:
            产生回答文本块的生成器
        """
        # 添加用户问题到消息列表
        self.messages.append({"role": "user", "content": question})
        
        # 准备创建参数
        create_params = {
            "model": model or self.model or self.client.default_model,
            "messages": self.messages.copy(),
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
        response_stream = self.client.client.chat.completions.create(**create_params)
        
        # 收集回答内容
        answer_chunks = []
        
        # 逐块处理回答
        for chunk in response_stream:
            if not chunk.choices:
                continue
            content = chunk.choices[0].delta.content
            if content:
                answer_chunks.append(content)
                yield content
        
        # 合并所有块得到完整回答
        answer = "".join(answer_chunks)
        
        # 将回答添加到消息列表
        self.messages.append({"role": "assistant", "content": answer})
        
        # 同时更新历史记录（不包含系统消息）
        if len(self.messages) > 1:
            self.history = self.messages[1:]
    
    def clear(self) -> None:
        """
        清除会话历史，但保留系统消息
        """
        # 只保留系统消息
        self.messages = [self.messages[0]]
        self.history = []
    
    def get_history(self) -> List[Dict[str, str]]:
        """
        获取会话历史
        
        返回:
            会话历史列表（不包含系统消息）
        """
        return self.history.copy()
    
    def think(
        self,
        question: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Tuple[str, str]:
        """
        在会话中发送问题并获取思考过程和回答
        
        参数:
            question: 要询问的问题
            model: 要使用的模型
            temperature: 生成的随机性，0-1 之间的值
            max_tokens: 生成的最大标记数
            **kwargs: 传递给 OpenAI API 的其他参数
            
        返回:
            (思考过程, 最终回答) 的元组
        """
        # 使用客户端的 think 方法，传入会话历史
        reasoning, answer = self.client.think(
            question=question,
            messages=self.messages,
            model=model or self.model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # 将问题和回答添加到会话历史
        self.messages.append({"role": "user", "content": question})
        self.messages.append({"role": "assistant", "content": answer})
        
        return reasoning, answer
    
    def stream_think(
        self,
        question: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Generator[Union[Tuple[str, None], Tuple[None, str]], None, None]:
        """
        在会话中发送问题并流式获取思考过程和回答
        
        参数:
            参数与 think 方法相同
            
        返回:
            生成器，产生 (思考内容, None) 或 (None, 回答内容) 的元组
        """
        # 收集完整的回答
        answer_content = ""
        
        # 使用客户端的 stream_think 方法
        for reasoning, answer in self.client.stream_think(
            question=question,
            messages=self.messages,
            model=model or self.model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        ):
            if answer is not None:
                answer_content += answer
            yield reasoning, answer
        
        # 将问题和完整回答添加到会话历史
        self.messages.append({"role": "user", "content": question})
        self.messages.append({"role": "assistant", "content": answer_content})
    
    def ask_json(
        self,
        question: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        在会话中发送问题并获取 JSON 格式的回答
        
        参数:
            question: 要询问的问题
            model: 要使用的模型（覆盖会话默认模型）
            temperature: 生成的随机性，0-1 之间的值
            max_tokens: 生成的最大标记数
            **kwargs: 传递给 OpenAI API 的其他参数
            
        返回:
            JSON 格式的回答
        """
        # 使用客户端的 ask_json 方法，传入会话历史
        response = self.client.ask_json(
            question=question,
            messages=self.messages,
            model=model or self.model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # 将问题和回答添加到消息列表
        self.messages.append({"role": "user", "content": question})
        # 将 JSON 响应转换为字符串存储
        import json
        self.messages.append({"role": "assistant", "content": json.dumps(response, ensure_ascii=False)})
        
        # 同时更新历史记录（不包含系统消息）
        if len(self.messages) > 1:
            self.history = self.messages[1:]
        
        return response 