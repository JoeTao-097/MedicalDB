#!/usr/bin/env python3
"""
医美数据管理系统 - 快速启动脚本
"""

import os
import sys
import subprocess
import time
import threading
from pathlib import Path
from backend.models import init_db

init_db()

def print_banner():
    """打印启动横幅"""
    print("""
🏥 医美数据管理系统
═══════════════════════════════════════════════════════════════
    """)

def check_environment():
    """检查环境"""
    print("🔍 检查运行环境...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ Python版本过低，需要Python 3.8+")
        return False
    
    # 检查必要文件
    required_files = [
        "backend/main.py",
        "frontend/app.py",
        ".env"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ 缺少必要文件: {file_path}")
            return False
    
    print("✅ 环境检查通过")
    return True

def install_dependencies():
    """安装依赖"""
    print("📦 安装依赖包...")
    
    try:
        # 安装后端依赖
        print("   📦 安装后端依赖...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"], 
                      check=True, capture_output=True)
        
        # 安装前端依赖
        print("   📦 安装前端依赖...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "frontend/requirements.txt"], 
                      check=True, capture_output=True)
        
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def setup_environment():
    """设置环境"""
    print("⚙️  设置环境...")
    
    # 检查.env文件
    if not Path(".env").exists():
        if Path(".env").exists():
            print("   📝 创建环境配置文件...")
            subprocess.run(["cp", ".env", ".env"])
            print("   ⚠️  请编辑 .env 文件配置数据库信息")
        else:
            print("❌ 未找到环境配置文件模板")
            return False
    
    print("✅ 环境设置完成")
    return True

def start_backend():
    """启动后端服务"""
    print("🚀 启动后端服务...")
    
    try:
        # 启动uvicorn（切换到backend目录）
        os.chdir('backend')
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
        
        # 等待服务启动
        time.sleep(5)
        
        print("✅ 后端服务启动成功")
        print("   📖 API文档: http://localhost:8000/docs")
        print("   🔗 健康检查: http://localhost:8000/")
        
        return process
    except Exception as e:
        print(f"❌ 后端服务启动失败: {e}")
        return None

def start_frontend():
    """启动前端服务"""
    print("🚀 启动前端服务...")
    
    try:
        # 启动streamlit（切换到frontend目录）
        os.chdir('../frontend')
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ])
        
        # 等待服务启动
        time.sleep(3)
        
        print("✅ 前端服务启动成功")
        print("   📱 前端界面: http://localhost:8501")
        
        return process
    except Exception as e:
        print(f"❌ 前端服务启动失败: {e}")
        return None

def create_sample_data():
    """创建示例数据"""
    print("📊 创建示例数据...")
    
    try:
        result = subprocess.run([sys.executable, "init_sample_data.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 示例数据创建成功")
            return True
        else:
            print(f"⚠️  示例数据创建失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 示例数据创建失败: {e}")
        return False

def main():
    """主函数"""
    print_banner()
    
    # 检查环境
    if not check_environment():
        return
    
    # 设置环境
    if not setup_environment():
        return
    
    # 询问是否安装依赖
    install_deps = input("是否安装依赖包？(y/n): ").lower().strip()
    if install_deps in ['y', 'yes', '是']:
        if not install_dependencies():
            return
    
    # 询问是否创建示例数据
    create_data = input("是否创建示例数据？(y/n): ").lower().strip()
    if create_data in ['y', 'yes', '是']:
        create_sample_data()
    
    print("\n🎯 启动服务...")
    print("⏳ 正在启动后端和前端服务...")
    
    # 启动后端
    backend_process = start_backend()
    if not backend_process:
        return
    
    # 等待后端完全启动
    time.sleep(3)
    
    # 启动前端
    frontend_process = start_frontend()
    if not frontend_process:
        backend_process.terminate()
        return
    
    print("\n🎉 系统启动完成！")
    print("═══════════════════════════════════════════════════════════════")
    print("📱 前端界面: http://localhost:8501")
    print("📖 API文档: http://localhost:8000/docs")
    print("🔗 健康检查: http://localhost:8000/")
    print("═══════════════════════════════════════════════════════════════")
    print("⏹️  按 Ctrl+C 停止所有服务")
    
    try:
        # 等待用户中断
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 正在停止服务...")
        
        # 停止前端
        if frontend_process:
            frontend_process.terminate()
            print("✅ 前端服务已停止")
        
        # 停止后端
        if backend_process:
            backend_process.terminate()
            print("✅ 后端服务已停止")
        
        print("👋 所有服务已停止")

if __name__ == "__main__":
    main() 