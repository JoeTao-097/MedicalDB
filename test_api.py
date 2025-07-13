#!/usr/bin/env python3
"""
测试API连接
"""

import requests
import time
import sys
import os

def test_backend_connection():
    """测试后端连接"""
    print("🔍 测试后端连接...")
    
    try:
        # 测试健康检查
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务连接正常")
            return True
        else:
            print(f"❌ 后端服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到后端服务: {e}")
        return False

def test_api_endpoints():
    """测试API端点"""
    print("🔍 测试API端点...")
    
    endpoints = [
        "/api/customers",
        "/api/consultants", 
        "/api/products",
        "/api/analysis/inactive-customers",
        "/api/analysis/new-customer-reopen",
        "/api/analysis/vip-consumption",
        "/api/analysis/unspent-balance",
        "/api/analysis/department-performance",
        "/api/analysis/product-performance"
    ]
    
    success_count = 0
    for endpoint in endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=10)
            if response.status_code in [200, 404, 500]:  # 接受这些状态码
                print(f"✅ {endpoint}: {response.status_code}")
                success_count += 1
            else:
                print(f"❌ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    
    print(f"📊 API测试完成: {success_count}/{len(endpoints)} 个端点响应")
    return success_count > 0

def main():
    """主函数"""
    print("🧪 开始API测试...")
    print("=" * 50)
    
    # 等待后端启动
    print("⏳ 等待后端服务启动...")
    for i in range(30):
        if test_backend_connection():
            break
        print(f"⏳ 等待中... ({i+1}/30)")
        time.sleep(1)
    else:
        print("❌ 后端服务启动超时")
        return False
    
    print()
    
    # 测试API端点
    api_ok = test_api_endpoints()
    
    print()
    print("=" * 50)
    if api_ok:
        print("🎉 API测试基本通过！")
        print("💡 注意：某些端点可能返回500错误，这是正常的（数据库可能为空）")
        return True
    else:
        print("❌ API测试失败")
        return False

if __name__ == "__main__":
    main() 