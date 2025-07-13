#!/usr/bin/env python3
"""
调试阿里百炼API响应结构
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def debug_qwen_response():
    """调试阿里百炼API响应"""
    try:
        import dashscope
        
        # 设置API密钥
        api_key = os.getenv('DASHSCOPE_API_KEY')
        if not api_key:
            print("❌ 未设置 DASHSCOPE_API_KEY 环境变量")
            return
        
        dashscope.api_key = api_key
        
        print("🔍 测试阿里百炼API调用...")
        
        # 简单测试
        response = dashscope.Generation.call(
            model='qwen-max',
            messages=[
                {"role": "user", "content": "你好"}
            ]
        )
        
        print(f"响应类型: {type(response)}")
        print(f"响应内容: {response}")
        
        if hasattr(response, 'status_code'):
            print(f"状态码: {response.status_code}")
        
        if hasattr(response, 'output'):
            print(f"output存在: {response.output}")
            if response.output is not None:
                print(f"output类型: {type(response.output)}")
                if hasattr(response.output, 'choices'):
                    print(f"choices存在: {response.output.choices}")
                    if response.output.choices is not None:
                        print(f"choices长度: {len(response.output.choices)}")
                        if len(response.output.choices) > 0:
                            choice = response.output.choices[0]
                            print(f"第一个choice: {choice}")
                            if hasattr(choice, 'message'):
                                print(f"message: {choice.message}")
                                if hasattr(choice.message, 'content'):
                                    print(f"content: {choice.message.content}")
        
        if hasattr(response, 'message'):
            print(f"错误信息: {response.message}")
            
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_qwen_response() 