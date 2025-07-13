#!/usr/bin/env python3
"""
医美数据管理系统 - 前端启动脚本
"""

import os
import sys
import subprocess
import requests
import time
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import streamlit
        import requests
        import pandas
        import plotly
        print("✅ 前端依赖检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r frontend/requirements.txt")
        return False

def check_backend_service():
    """检查后端服务是否运行"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务连接正常")
            return True
        else:
            print("❌ 后端服务响应异常")
            return False
    except requests.exceptions.RequestException:
        print("❌ 无法连接到后端服务")
        print("请先启动后端服务: python start_backend.py")
        return False

def wait_for_backend():
    """等待后端服务启动"""
    print("⏳ 等待后端服务启动...")
    for i in range(30):  # 等待30秒
        try:
            response = requests.get("http://localhost:8000/", timeout=2)
            if response.status_code == 200:
                print("✅ 后端服务已就绪")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"⏳ 等待中... ({i+1}/30)")
        time.sleep(1)
    
    print("❌ 后端服务启动超时")
    return False

def start_frontend():
    """启动前端服务"""
    print("🚀 启动医美数据管理系统前端...")
    
    # 检查依赖
    if not check_dependencies():
        return False
    
    # 检查后端服务
    if not check_backend_service():
        print("🔄 尝试等待后端服务启动...")
        if not wait_for_backend():
            return False
    
    # 启动服务
    try:
        print("🌐 启动Streamlit服务...")
        print("📱 前端界面地址: http://localhost:8501")
        print("⏹️  按 Ctrl+C 停止服务")
        
        # 启动streamlit（切换到frontend目录）
        os.chdir('frontend')
        subprocess.run([
            "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_frontend() 