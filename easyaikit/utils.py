"""
EasyOpenAI 工具模块 - 提供便捷的辅助功能
"""

import os
import sys
from typing import List, Dict, Optional, Union, TextIO, Generator, Callable, Any


def print_stream_to_console(content_stream: Generator[str, None, None], end: str = "") -> None:
    """
    将流式内容打印到控制台
    
    参数:
        content_stream: 内容流，来自 stream_ask
        end: 结束后添加的字符
    """
    for chunk in content_stream:
        print(chunk, end="", flush=True)
    print(end)


def save_stream_to_file(content_stream: Generator[str, None, None], file_path: str) -> None:
    """
    将流式内容保存到文件
    
    参数:
        content_stream: 内容流，来自 stream_ask
        file_path: 要保存的文件路径
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        for chunk in content_stream:
            f.write(chunk)


def stream_with_callback(
    content_stream: Generator[str, None, None], 
    callback: Callable[[str], Any], 
    *args: Any, 
    **kwargs: Any
) -> str:
    """
    对流式内容应用回调函数，同时返回完整内容
    
    参数:
        content_stream: 内容流，来自 stream_ask
        callback: 回调函数，接受一个字符串块和其他参数
        *args, **kwargs: 传递给回调函数的其他参数
        
    返回:
        完整的内容字符串
    """
    full_content = ""
    for chunk in content_stream:
        callback(chunk, *args, **kwargs)
        full_content += chunk
    return full_content


def format_history(messages: List[Dict[str, str]]) -> str:
    """
    格式化对话历史以便于显示
    
    参数:
        messages: 对话消息列表
        
    返回:
        格式化的对话历史字符串
    """
    result = ""
    for msg in messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        if role == "system":
            result += f"[系统]: {content}\n\n"
        elif role == "user":
            result += f"[用户]: {content}\n\n"
        elif role == "assistant":
            result += f"[助手]: {content}\n\n"
        else:
            result += f"[{role}]: {content}\n\n"
    return result


def create_conversation_from_pairs(user_messages: List[str], assistant_messages: List[str]) -> List[Dict[str, str]]:
    """
    从用户消息和助手回复对创建对话历史
    
    参数:
        user_messages: 用户消息列表
        assistant_messages: 助手回复列表（长度应该等于或比用户消息少1）
        
    返回:
        格式化的对话历史列表
    """
    if len(assistant_messages) > len(user_messages):
        raise ValueError("助手回复的数量不能超过用户消息的数量")
    
    conversation = []
    for i in range(len(user_messages)):
        conversation.append({"role": "user", "content": user_messages[i]})
        if i < len(assistant_messages):
            conversation.append({"role": "assistant", "content": assistant_messages[i]})
    
    return conversation 