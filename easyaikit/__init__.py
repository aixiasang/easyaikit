"""
EasyOpenAI - 简化的 OpenAI API 封装
"""

from easyopenai.client import AI, ask, stream_ask
from easyopenai.session import ChatSession

__version__ = "0.1.0"
__all__ = ["AI", "ChatSession", "ask", "stream_ask"] 