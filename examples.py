"""
EasyOpenAI 使用示例
"""

import os
import time
from easyaikit import AI, ask, stream_ask
from easyaikit.utils import print_stream_to_console, save_stream_to_file, format_history

# 确保设置了环境变量
os.environ["ARK_API_KEY"] = "设置你的APIKEY"

def basic_example():
    """基本用法示例"""
    print("\n=== 基本用法示例 ===")
    
    # 方法 1: 使用便捷函数
    print("\n1. 使用便捷函数:")
    response = ask("什么是机器学习？")
    print(response)
    
    # 方法 2: 使用客户端实例
    print("\n2. 使用客户端实例:")
    client = AI()
    response = client.ask("什么是深度学习？")
    print(response)


def streaming_example():
    """流式响应示例"""
    print("\n=== 流式响应示例 ===")
    
    client = AI()
    
    print("\n1. 基本流式响应:")
    print("回答: ", end="")
    for chunk in client.stream_ask("简单介绍一下Python编程语言"):
        print(chunk, end="", flush=True)
        time.sleep(0.01)  # 增加一点延迟，以便于观察流式效果
    print()
    
    print("\n2. 使用工具函数处理流式响应:")
    stream = client.stream_ask("列出五种常见的编程范式")
    print_stream_to_console(stream, end="\n\n")
    
    print("\n3. 保存流式响应到文件:")
    stream = client.stream_ask("编写一个简单的Python函数来计算斐波那契数列")
    save_stream_to_file(stream, "fibonacci.py")
    print("响应已保存到 fibonacci.py")


def session_example():
    """会话示例"""
    print("\n=== 会话示例 ===")
    
    client = AI()
    
    # 创建会话
    print("\n创建会话:")
    session = client.session(system_message="你是一位人工智能专家")
    
    # 第一轮对话
    print("\n第一轮对话:")
    response = session.ask("什么是神经网络？")
    print(response)
    
    # 第二轮对话（使用前一轮的上下文）
    print("\n第二轮对话（上下文已保存）:")
    response = session.ask("它们有哪些实际应用？")
    print(response)
    
    # 第三轮对话（使用流式响应）
    print("\n第三轮对话（使用流式响应）:")
    print("回答: ", end="")
    for chunk in session.stream_ask("神经网络与传统算法相比有什么优势？"):
        print(chunk, end="", flush=True)
    print("\n")
    
    # 查看会话历史
    print("\n会话历史:")
    history = session.get_history()
    print(format_history(history))
    
    # 清除会话历史
    print("\n清除会话历史:")
    session.clear()
    print("历史已清除，会话被重置")


def think_example():
    """思考过程示例"""
    print("\n=== 思考过程示例 ===")
    
    client = AI()
    
    # 1. 使用 think 方法
    print("\n1. 使用 think 方法:")
    print("\n问题: 9.9和9.11谁大？")
    reasoning, answer = client.think("9.9和9.11谁大？")
    
    print("\n思考过程:")
    print(reasoning)
    print("\n最终回答:")
    print(answer)
    
    # 2. 使用 stream_think 方法
    print("\n2. 使用 stream_think 方法:")
    print("\n问题: 1.5和1.05谁大？")
    
    print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")
    reasoning_content = ""
    answer_content = ""
    is_answering = False
    
    for reasoning, answer in client.stream_think("1.5和1.05谁大？"):
        if reasoning is not None:
            print(reasoning, end="", flush=True)
            reasoning_content += reasoning
        elif answer is not None:
            if not is_answering:
                print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
                is_answering = True
            print(answer, end="", flush=True)
            answer_content += answer
    print("\n")
    
    # 3. 在会话中使用思考过程
    print("\n3. 在会话中使用思考过程:")
    session = client.session(system_message="你是一位数学老师")
    
    print("\n第一个问题: 0.5和0.05的关系是什么？")
    reasoning, answer = session.think("0.5和0.05的关系是什么？")
    
    print("\n思考过程:")
    print(reasoning)
    print("\n最终回答:")
    print(answer)
    
    print("\n第二个问题: 它们相差多少倍？")
    reasoning, answer = session.think("它们相差多少倍？")
    
    print("\n思考过程:")
    print(reasoning)
    print("\n最终回答:")
    print(answer)


def db_storage_example():
    """数据库存储示例"""
    print("\n=== 数据库存储示例 ===")
    
    client = AI()
    
    # 加载数据库存储
    print("\n1. 创建数据库存储:")
    db = client.load_db("chat.db")
    print("数据库已创建")
    
    # 保存一些消息
    print("\n2. 保存消息:")
    db.save_message("user", "什么是机器学习？")
    response = client.ask("什么是机器学习？")
    db.save_message("assistant", response)
    print("消息已保存")
    
    # 查看所有会话
    print("\n3. 查看所有会话:")
    sessions = db.view_sessions()
    for session in sessions:
        print(f"会话ID: {session['session_id']}")
        print(f"创建时间: {session['created_at']}")
        print(f"消息数量: {session['message_count']}")
        print()
    
    # 查看当前会话的消息
    print("\n4. 查看当前会话的消息:")
    messages = db.view_session_messages()
    for msg in messages:
        print(f"[{msg['role']}]: {msg['content'][:100]}...")
        print(f"时间: {msg['created_at']}")
        print()
    
    # 创建新的会话
    print("\n5. 创建新的会话:")
    new_session_id = db.load_session(db.session_id, update=True)
    print(f"新会话ID: {new_session_id}")
    
    # 在新会话中保存消息
    db.save_message("user", "深度学习是什么？")
    response = client.ask("深度学习是什么？")
    db.save_message("assistant", response)
    print("新会话消息已保存")


def json_storage_example():
    """JSON 存储示例"""
    print("\n=== JSON 存储示例 ===")
    
    client = AI()
    
    # 加载 JSON 存储
    print("\n1. 创建 JSON 存储:")
    js = client.load_json("chat.json")
    print("JSON 文件已创建")
    
    # 保存一些消息
    print("\n2. 保存消息:")
    js.save_message("user", "Python 有哪些特点？")
    response = client.ask("Python 有哪些特点？")
    js.save_message("assistant", response)
    print("消息已保存")
    
    # 查看所有会话
    print("\n3. 查看所有会话:")
    sessions = js.view_sessions()
    for session in sessions:
        print(f"会话ID: {session['session_id']}")
        print(f"创建时间: {session['created_at']}")
        print(f"消息数量: {session['message_count']}")
        print()
    
    # 查看当前会话的消息
    print("\n4. 查看当前会话的消息:")
    messages = js.view_session_messages()
    for msg in messages:
        print(f"[{msg['role']}]: {msg['content'][:100]}...")
        print(f"时间: {msg['created_at']}")
        print()
    
    # 创建新的会话
    print("\n5. 创建新的会话:")
    new_session_id = js.load_session(js.session_id, update=True)
    print(f"新会话ID: {new_session_id}")
    
    # 在新会话中保存消息
    js.save_message("user", "什么是人工智能？")
    response = client.ask("什么是人工智能？")
    js.save_message("assistant", response)
    print("新会话消息已保存")


def custom_options_example():
    """自定义选项示例"""
    print("\n=== 自定义选项示例 ===")
    
    # 自定义客户端选项
    client = AI(
        system_message="你是一位专业的创意写作者",
        max_retries=3
    )
    
    # 使用自定义请求参数
    print("\n使用更高创造性的设置:")
    response = client.ask(
        "写一个短篇故事，主题是'意外的发现'",
        temperature=0.8,  # 更高的创造性
        max_tokens=300,   # 限制响应长度
        top_p=0.95        # 更多样化的输出
    )
    print(response)
    
    # 在会话中使用不同的系统消息
    print("\n在会话中使用不同的系统消息:")
    session = client.session(
        system_message="你是一位物理学教授，专长于用简单的语言解释复杂的概念"
    )
    response = session.ask("解释量子力学的基本原理")
    print(response)


def json_response_example():
    """JSON 响应示例"""
    print("\n=== JSON 响应示例 ===")
    
    client = AI()
    
    # 1. 基本 JSON 响应
    print("\n1. 基本 JSON 响应:")
    print("\n问题: 分析以下数字：1, 2, 3, 4, 5")
    response = client.ask_json(
        "分析这组数字：1, 2, 3, 4, 5。请提供：\n"
        "1. 基本统计信息（总和、平均值、最大值、最小值）\n"
        "2. 数据特征（是否连续、是否等差数列）"
    )
    
    print("\nJSON 响应:")
    import json
    print(json.dumps(response, ensure_ascii=False, indent=2))
    
    # 检查是否有错误
    if "error" in response:
        print("\n警告：获取JSON响应时出现错误:")
        print(f"错误信息: {response['message']}")
        print(f"原始响应: {response['raw_response']}")
    
    # 2. 在会话中使用 JSON 响应
    print("\n2. 在会话中使用 JSON 响应:")
    session = client.session(system_message="你是一位数据分析专家")
    
    print("\n第一个问题: 分析两个数组")
    response = session.ask_json(
        "分析这两个数组：[1,2,3] 和 [4,5,6]。请提供：\n"
        "1. 每个数组的基本统计信息（总和、平均值）\n"
        "2. 两个数组的对比分析"
    )
    
    print("\nJSON 响应:")
    if "error" not in response:
        print(json.dumps(response, ensure_ascii=False, indent=2))
    else:
        print("错误：", response["message"])
    
    print("\n第二个问题: 数组比较")
    response = session.ask_json(
        "基于前面的分析，请提供：\n"
        "1. 两个数组的元素之和的比较\n"
        "2. 两个数组的平均值的比较\n"
        "3. 增长趋势分析"
    )
    
    print("\nJSON 响应:")
    if "error" not in response:
        print(json.dumps(response, ensure_ascii=False, indent=2))
    else:
        print("错误：", response["message"])


def main():
    """运行所有示例"""
    # basic_example()
    # streaming_example()
    # session_example()
    # think_example()
    json_response_example()
    # db_storage_example()
    # json_storage_example()
    # custom_options_example()


if __name__ == "__main__":
    main() 