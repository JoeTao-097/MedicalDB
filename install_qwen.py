#!/usr/bin/env python3
"""
安装阿里百炼Qwen3依赖
"""

import subprocess
import sys
import os
from pathlib import Path

def install_dashscope():
    """安装dashscope库"""
    print("📦 安装阿里百炼SDK...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "dashscope==1.14.0"], 
                      check=True, capture_output=True)
        print("✅ dashscope 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ dashscope 安装失败: {e}")
        return False

def update_env_file():
    """更新环境配置文件"""
    env_file = Path(".env")
    env_example = Path("env_example")
    
    if not env_file.exists() and env_example.exists():
        print("📝 创建环境配置文件...")
        subprocess.run(["cp", "env_example", ".env"])
        print("✅ 环境配置文件已创建")
        print("⚠️  请编辑 .env 文件，设置你的 DASHSCOPE_API_KEY")
    elif env_file.exists():
        print("📝 更新环境配置文件...")
        # 读取现有配置
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换OpenAI配置为阿里百炼配置
        if 'OPENAI_API_KEY' in content:
            content = content.replace(
                '# OpenAI API配置\nOPENAI_API_KEY=your_openai_api_key_here',
                '# 阿里百炼API配置\nDASHSCOPE_API_KEY=your_dashscope_api_key_here'
            )
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ 环境配置文件已更新")
            print("⚠️  请编辑 .env 文件，设置你的 DASHSCOPE_API_KEY")
        else:
            print("✅ 环境配置文件已存在")
    else:
        print("❌ 未找到环境配置文件模板")

def main():
    """主函数"""
    print("🚀 安装阿里百炼Qwen3依赖...")
    
    # 安装dashscope
    if not install_dashscope():
        return
    
    # 更新环境配置
    update_env_file()
    
    print("\n🎉 安装完成！")
    print("\n📋 后续步骤:")
    print("1. 编辑 .env 文件，设置你的 DASHSCOPE_API_KEY")
    print("2. 运行: python test_qwen.py 测试集成")
    print("3. 重启后端服务以应用更改")
    print("\n🔗 获取API密钥:")
    print("访问: https://dashscope.console.aliyun.com/")
    print("创建API密钥并复制到 .env 文件中")

if __name__ == "__main__":
    main() 