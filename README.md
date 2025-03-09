# EasyAIKit

一个简单易用的 AI API 工具包，让 AI 调用更轻松。专为中文用户优化的接口设计，支持流式响应、会话管理、数据持久化等丰富功能。

## 特点

- 简单直观的接口设计
- 支持流式响应
- 内置会话管理
- 支持数据持久化（数据库和JSON）
- 支持思考过程分离
- 支持 JSON 格式响应
- 完整的类型提示
- 详细的文档说明

## 安装

```bash
pip install easyaikit
```

## 快速开始

### 作为库使用

```python
from easyaikit import AI, ask, stream_ask

# 方式 1: 使用便捷函数
response = ask("什么是机器学习？")
print(response)

# 方式 2: 使用客户端类
client = AI()
response = client.ask("什么是机器学习？")
print(response)

# 流式响应
for chunk in stream_ask("简单介绍一下Python"):
    print(chunk, end="")
```

### 使用会话接口

```python
from easyaikit import AI

# 创建客户端
client = AI()

# 创建会话
session = client.session()

# 第一轮对话
response = session.ask("什么是神经网络？")
print(response)

# 第二轮对话（自动保持上下文）
response = session.ask("它们有哪些实际应用？")
print(response)

# 第三轮对话（使用流式输出）
for chunk in session.stream_ask("与传统算法相比有什么优势？"):
    print(chunk, end="")

# 查看会话历史
history = session.get_history()
```

### 作为命令行工具使用

```bash
# 基本用法
easyai "什么是机器学习？"

# 流式输出
easyai --stream "简单介绍一下Python"

# 自定义系统消息
easyai --system "你是一位诗人" "写一首关于春天的诗"

# 保存到文件
easyai "什么是量子计算？" --output quantum.txt
```

## 高级用法

### 自定义选项

```python
from easyaikit import AI

# 自定义客户端选项
client = AI(
    api_key="your-api-key",
    base_url="https://custom-api-endpoint.com",
    default_model="your-preferred-model",
    system_message="自定义的默认系统消息",
    timeout=30.0,
    max_retries=5
)

# 自定义请求选项
response = client.ask(
    "给我讲个故事",
    temperature=0.8,
    max_tokens=500,
    top_p=0.95
)
print(response)
```

### 工具函数

```python
from easyaikit import AI
from easyaikit.utils import save_stream_to_file, print_stream_to_console, format_history

client = AI()

# 保存流式响应到文件
stream = client.stream_ask("写一篇短文")
save_stream_to_file(stream, "output.txt")

# 打印带格式的对话历史
session = client.session()
session.ask("你好")
session.ask("今天天气怎么样？")
history = session.get_history()
print(format_history(history))
```

## API 参考

### `AI` 类

```python
def __init__(self, api_key=None, base_url=None, default_model=None, system_message="你是人工智能助手", timeout=None, max_retries=2)
```

### 主要方法

- `ask(question, system_message=None, model=None, temperature=None, max_tokens=None, **kwargs)` - 发送问题并获取回答
- `stream_ask(question, system_message=None, model=None, temperature=None, max_tokens=None, **kwargs)` - 发送问题并流式获取回答
- `session(system_message=None, model=None)` - 创建一个新的对话会话
- `get_openai_client()` - 获取底层的 OpenAI 客户端实例

### `ChatSession` 类

```python
def __init__(self, client, system_message="你是人工智能助手", model=None)
```

- `ask(question, model=None, temperature=None, max_tokens=None, **kwargs)` - 在会话中发送问题并获取回答
- `stream_ask(question, model=None, temperature=None, max_tokens=None, **kwargs)` - 在会话中发送问题并流式获取回答
- `clear()` - 清除会话历史
- `get_history()` - 获取会话历史

### 便捷函数

- `ask(question, api_key=None, model=None, system_message=None, **kwargs)` - 发送问题并获取回答
- `stream_ask(question, api_key=None, model=None, system_message=None, **kwargs)` - 发送问题并流式获取回答

### 工具函数

- `print_stream_to_console(content_stream, end="")` - 将流式内容打印到控制台
- `save_stream_to_file(content_stream, file_path)` - 将流式内容保存到文件
- `stream_with_callback(content_stream, callback, *args, **kwargs)` - 对流式内容应用回调函数
- `format_history(messages)` - 格式化对话历史以便于显示

## 思考过程

```python
# 获取思考过程和答案
reasoning, answer = client.think("9.9和9.11谁大？")
print("思考过程:", reasoning)
print("最终答案:", answer)

# 流式获取思考过程
for reasoning, answer in client.stream_think("1.5和1.05谁大？"):
    if reasoning:
        print("思考:", reasoning, end="")
    if answer:
        print("答案:", answer, end="")
```

## JSON 响应

```python
# 获取 JSON 格式的响应
response = client.ask_json("分析这组数字：1, 2, 3, 4, 5")
print(response)
# 输出示例:
# {
#   "statistics": {
#     "sum": 15,
#     "average": 3,
#     "max": 5,
#     "min": 1
#   },
#   "features": {
#     "is_consecutive": true,
#     "is_arithmetic_sequence": true,
#     "common_difference": 1
#   }
# }

# 在会话中使用 JSON 响应
session = client.session()
response = session.ask_json("分析两个数组：[1,2,3] 和 [4,5,6]")
print(response)
```

## 数据持久化

```python
# 使用数据库存储
db = client.load_db("chat.db")
session = client.session()
session.set_storage(db)

# 使用 JSON 文件存储
js = client.load_json("chat.json")
session = client.session()
session.set_storage(js)
```

## 高级配置

```python
# 自定义配置
client = AI(
    api_key="your-api-key",
    base_url="your-api-base-url",
    default_model="your-model",
    system_message="自定义系统消息",
    timeout=30,
    max_retries=3
)

# 创建自定义会话
session = client.session(
    system_message="你是一位物理学教授",
    model="specific-model",
    temperature=0.7,
    max_tokens=2000
)
```

## 便捷函数

```python
from easyaikit import ask, stream_ask

# 快速提问
response = ask("什么是人工智能？")
print(response)

# 快速流式提问
for chunk in stream_ask("解释一下量子计算"):
    print(chunk, end="")
```

## 工具函数

```python
from easyaikit.utils import print_stream_to_console, save_stream_to_file

# 打印流式响应
stream = client.stream_ask("讲个故事")
print_stream_to_console(stream)

# 保存流式响应到文件
stream = client.stream_ask("写一个Python脚本")
save_stream_to_file(stream, "script.py")
```

## 许可证

MIT License 