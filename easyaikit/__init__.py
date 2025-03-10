"""
EasyAIKit - 简单易用的 AI API 工具包
"""

# 从 client 模块导入核心类和函数
from easyaikit.client import AI, ask, stream_ask, think, stream_think, ask_json

# 从 session 模块导入会话相关类
from easyaikit.session import ChatSession

# 从 storage 模块导入存储相关类
from easyaikit.storage import DBStorage, JSONStorage

# 从 utils 模块导入工具函数
from easyaikit.utils import (
    print_stream_to_console,
    save_stream_to_file,
    format_history,
    stream_with_callback
)

__version__ = "0.1.1"
__all__ = [
    # 核心类和函数
    "AI", 
    "ask", 
    "stream_ask",
    
    # 会话相关
    "ChatSession",
    
    # 存储相关
    "DBStorage",
    "JSONStorage",
    
    # 工具函数
    "print_stream_to_console",
    "save_stream_to_file", 
    "format_history",
    "stream_with_callback"
] 