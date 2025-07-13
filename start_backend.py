#!/usr/bin/env python3
"""
医美数据管理系统 - 后端启动脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pymysql
        import pydantic
        print("✅ 后端依赖检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r backend/requirements.txt")
        return False

def check_env_file():
    """检查环境变量文件"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  未找到 .env 文件")
        print("请复制 env_example 为 .env 并配置数据库信息")
        return False
    print("✅ 环境变量文件检查通过")
    return True

def init_database():
    """初始化数据库"""
    try:
        sys.path.append('backend')
        from models import init_db
        init_db()
        print("✅ 数据库初始化完成")
        return True
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False

def start_backend():
    """启动后端服务"""
    print("🚀 启动医美数据管理系统后端...")
    
    # 检查依赖
    if not check_dependencies():
        return False
    
    # 检查环境配置
    if not check_env_file():
        return False
    
    # 初始化数据库
    if not init_database():
        return False
    
    # 启动服务
    try:
        print("🌐 启动FastAPI服务...")
        print("📖 API文档地址: http://localhost:8000/docs")
        print("🔗 健康检查: http://localhost:8000/")
        print("⏹️  按 Ctrl+C 停止服务")
        
        # 启动uvicorn（切换到backend目录）
        os.chdir('backend')
        subprocess.run([
            "uvicorn", "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_backend() 