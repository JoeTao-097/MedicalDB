#!/usr/bin/env python3
"""
测试模块导入
"""

import sys
import os

def test_backend_imports():
    """测试后端模块导入"""
    print("🔍 测试后端模块导入...")
    
    try:
        # 添加backend目录到路径
        backend_dir = os.path.join(os.getcwd(), 'backend')
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        
        # 测试导入
        from database import get_engine, get_session
        print("✅ database模块导入成功")
        
        from models import Customer, Consultant, MedicalProduct
        print("✅ models模块导入成功")
        
        from schemas import CustomerCreate, CustomerUpdate
        print("✅ schemas模块导入成功")
        
        from text2sql import Text2SQLConverter
        print("✅ text2sql模块导入成功")
        
        from business_analysis import BusinessAnalyzer
        print("✅ business_analysis模块导入成功")
        
        print("✅ 所有后端模块导入成功")
        return True
        
    except ImportError as e:
        print(f"❌ 后端模块导入失败: {e}")
        return False

def test_frontend_imports():
    """测试前端模块导入"""
    print("🔍 测试前端模块导入...")
    
    try:
        # 添加frontend目录到路径
        frontend_dir = os.path.join(os.getcwd(), 'frontend')
        if frontend_dir not in sys.path:
            sys.path.insert(0, frontend_dir)
        
        # 测试导入
        import streamlit as st
        print("✅ streamlit模块导入成功")
        
        # 测试页面模块
        from pages import natural_language_query, top_growth_points, data_management
        print("✅ pages模块导入成功")
        
        print("✅ 所有前端模块导入成功")
        return True
        
    except ImportError as e:
        print(f"❌ 前端模块导入失败: {e}")
        return False

def main():
    """主函数"""
    print("🧪 开始测试模块导入...")
    print("=" * 50)
    
    # 测试后端导入
    backend_ok = test_backend_imports()
    print()
    
    # 测试前端导入
    frontend_ok = test_frontend_imports()
    print()
    
    # 总结
    print("=" * 50)
    if backend_ok and frontend_ok:
        print("🎉 所有模块导入测试通过！")
        return True
    else:
        print("❌ 部分模块导入测试失败")
        return False

if __name__ == "__main__":
    main() 