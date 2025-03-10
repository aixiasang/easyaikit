"""
测试 easyaikit 包的导入
"""

# 测试核心类和函数导入
from easyaikit import (
    AI, 
    ask, 
    stream_ask,
    think, 
    stream_think,
    ask_json
)

# 测试会话相关类导入
from easyaikit import ChatSession

# 测试存储相关类导入
from easyaikit import DBStorage, JSONStorage

# 测试工具函数导入
from easyaikit import (
    print_stream_to_console,
    save_stream_to_file, 
    format_history,
    stream_with_callback
)

# 获取版本号
from easyaikit import __version__

print(f"所有导入都成功了！easyaikit 版本: {__version__}") 