#!/usr/bin/env python3
"""
测试阿里百炼Qwen3模型集成
"""

import os
import sys
from dotenv import load_dotenv

# 添加backend路径
sys.path.append('backend')

load_dotenv()

def test_qwen_integration():
    """测试阿里百炼集成"""
    try:
        import dashscope
        
        # 设置API密钥
        api_key = os.getenv('DASHSCOPE_API_KEY')
        if not api_key:
            print("❌ 未设置 DASHSCOPE_API_KEY 环境变量")
            print("请在 .env 文件中设置你的阿里百炼API密钥")
            return False
        
        dashscope.api_key = api_key
        
        # 测试简单查询
        response = dashscope.Generation.call(
            model='qwen-max',
            messages=[
                {"role": "user", "content": "你好，请简单介绍一下你自己"}
            ]
        )
        
        if response.status_code == 200:
            print("✅ 阿里百炼API连接成功")
            print(f"回复: {response.output.text}")
            return True
        else:
            print(f"❌ API调用失败: {response.message}")
            return False
            
    except ImportError:
        print("❌ 未安装 dashscope 库")
        print("请运行: pip install dashscope")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_sql_generation():
    """测试SQL生成功能"""
    try:
        from text2sql import text_to_sql
        
        test_query = "查询所有VIP顾客的消费记录"
        sql = text_to_sql(test_query)
        
        if sql.startswith("SQL生成错误"):
            print(f"❌ SQL生成失败: {sql}")
            return False
        else:
            print("✅ SQL生成成功")
            print(f"生成的SQL: {sql}")
            return True
            
    except Exception as e:
        print(f"❌ SQL生成测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🧪 测试阿里百炼Qwen3集成...")
    
    # 测试API连接
    if test_qwen_integration():
        print("\n🔍 测试SQL生成功能...")
        test_sql_generation()
    else:
        print("\n❌ API连接失败，跳过SQL生成测试")
    
    print("\n📝 使用说明:")
    print("1. 确保已在 .env 文件中设置 DASHSCOPE_API_KEY")
    print("2. 运行: pip install dashscope")
    print("3. 重启后端服务以应用更改") 