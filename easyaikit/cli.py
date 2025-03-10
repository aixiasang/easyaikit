"""
EasyOpenAI 命令行工具
"""


import argparse

from easyaikit.client import AI


def main():
    """
    EasyOpenAI 命令行入口点
    """
    parser = argparse.ArgumentParser(description="EasyOpenAI 命令行工具")
    parser.add_argument("query", help="要询问的问题")
    parser.add_argument("--stream", action="store_true", help="使用流式输出")
    parser.add_argument("--system", help="自定义系统消息")
    parser.add_argument("--model", help="要使用的模型")
    parser.add_argument("--api-key", help="API密钥（如果不想使用环境变量）")
    parser.add_argument("--base-url", help="API基础URL")
    parser.add_argument("--temperature", type=float, help="生成的随机性，0-1之间的值")
    parser.add_argument("--max-tokens", type=int, help="生成的最大标记数")
    parser.add_argument("--timeout", type=float, help="请求超时时间（秒）")
    parser.add_argument("--output", help="将输出保存到指定文件")
    parser.add_argument("--session", action="store_true", help="使用会话模式进行多轮对话")
    
    args = parser.parse_args()
    
    # 创建客户端
    client_kwargs = {}
    if args.api_key:
        client_kwargs["api_key"] = args.api_key
    if args.base_url:
        client_kwargs["base_url"] = args.base_url
    if args.model:
        client_kwargs["default_model"] = args.model
    if args.system:
        client_kwargs["system_message"] = args.system
    if args.timeout:
        client_kwargs["timeout"] = args.timeout
        
    client = AI(**client_kwargs)
    
    # 准备请求参数
    request_kwargs = {}
    if args.temperature is not None:
        request_kwargs["temperature"] = args.temperature
    if args.max_tokens is not None:
        request_kwargs["max_tokens"] = args.max_tokens
    
    # 执行请求并处理输出
    if args.session:
        print("会话模式尚未在命令行工具中实现。使用单次查询模式。")
    
    if args.stream:
        print("\n回答: ", end="", flush=True)
        stream = client.stream_ask(args.query, **request_kwargs)
        
        if args.output:
            # 将流式响应保存到文件
            with open(args.output, 'w', encoding='utf-8') as f:
                for chunk in stream:
                    print(chunk, end="", flush=True)
                    f.write(chunk)
        else:
            # 直接打印到控制台
            for chunk in stream:
                print(chunk, end="", flush=True)
        
        print()  # 打印换行
    else:
        response = client.ask(args.query, **request_kwargs)
        
        if args.output:
            # 保存到文件
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(response)
            print(f"回答已保存到文件: {args.output}")
        else:
            # 打印到控制台
            print(f"\n回答: {response}")


if __name__ == "__main__":
    main() 