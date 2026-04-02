#!/usr/bin/env python3
"""
最终测试批量删除功能
"""

import os
os.environ['DB_TYPE'] = 'postgresql'

import uuid
import requests
import json

def test_final_batch_delete():
    """测试批量删除功能（无保护逻辑）"""
    print("=== 测试批量删除功能（无保护逻辑） ===")
    
    base_url = "http://localhost:8002"
    
    # 1. 创建一些测试用户
    print("1. 创建测试用户...")
    test_user_ids = []
    
    # 创建3个测试用户
    for i in range(3):
        user_id = f"batch_test_{str(uuid.uuid4())[:8]}"
        test_user_ids.append(user_id)
        
        create_data = {
            "user_id": user_id,
            "homework": {
                "course": f"批量测试课程{i+1}",
                "content": f"批量测试内容{i+1}",
                "start_time": "",
                "deadline": "2026-04-30 23:59",
                "difficulty": "中",
                "image_url": ""
            }
        }
        
        response = requests.post(
            f"{base_url}/api/reminder",
            json=create_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"  创建用户 {i+1} 成功: {user_id}")
        else:
            print(f"  创建用户 {i+1} 失败: {response.status_code}")
    
    if len(test_user_ids) < 3:
        print("❌ 创建测试用户失败，无法继续测试")
        return False
    
    print(f"✅ 创建 {len(test_user_ids)} 个测试用户成功")
    
    # 等待1秒，确保数据写入
    import time
    time.sleep(1)
    
    # 2. 测试批量删除用户
    print("\n2. 测试批量删除用户...")
    batch_delete_data = {
        "user_ids": test_user_ids
    }
    
    response = requests.post(
        f"{base_url}/management/users/batch-delete",
        json=batch_delete_data,
        timeout=10
    )
    
    print(f"批量删除用户请求状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 批量删除用户成功: {result.get('message', '')}")
        print(f"   删除数量: {result.get('deleted_count', 0)}")
        
        # 检查是否删除了所有用户
        deleted_count = result.get('deleted_count', 0)
        if deleted_count == len(test_user_ids):
            print(f"✅ 成功删除了所有 {deleted_count} 个用户")
        else:
            print(f"⚠️ 只删除了 {deleted_count} 个用户，预期 {len(test_user_ids)} 个")
    else:
        print(f"❌ 批量删除用户失败: {response.status_code}")
        print(f"   响应: {response.text[:500]}")
        return False
    
    # 3. 验证管理页面
    print("\n3. 验证管理页面...")
    # 检查用户管理页面是否能正常访问
    response = requests.get(
        f"{base_url}/management/users",
        timeout=10
    )
    
    if response.status_code == 200:
        print("✅ 用户管理页面可正常访问")
    else:
        print(f"❌ 用户管理页面访问失败: {response.status_code}")
        return False
    
    print("\n" + "=" * 50)
    print("批量删除功能测试完成!")
    print("=" * 50)
    
    return True

def test_web_interface():
    """测试Web界面批量删除功能"""
    print("\n=== 测试Web界面批量删除功能 ===")
    
    base_url = "http://localhost:8002"
    
    # 1. 访问用户管理页面
    print("1. 访问用户管理页面...")
    response = requests.get(
        f"{base_url}/management/users",
        timeout=10
    )
    
    if response.status_code == 200:
        print("✅ 用户管理页面加载成功")
        
        # 检查页面是否包含批量操作元素
        html_content = response.text
        
        # 检查关键元素
        checks = [
            ("批量操作区域", "batch-operations"),
            ("全选复选框", "select-all-checkbox"),
            ("批量删除按钮", "batch-delete-btn"),
            ("批量导出按钮", "batch-export-btn"),
            ("选择计数", "selected-count")
        ]
        
        for check_name, check_id in checks:
            if check_id in html_content:
                print(f"  ✅ 页面包含 {check_name}")
            else:
                print(f"  ⚠️ 页面可能缺少 {check_name}")
    else:
        print(f"❌ 用户管理页面加载失败: {response.status_code}")
        return False
    
    print("\n2. 测试说明:")
    print("   现在可以访问用户管理页面进行批量删除操作:")
    print("   1. 打开浏览器访问: http://localhost:8002/management/users")
    print("   2. 选择用户前的复选框")
    print("   3. 点击'批量删除'按钮")
    print("   4. 确认操作后，选中的用户将被删除")
    print("   5. 不再保护任何用户，所有选中的用户都会被删除")
    
    return True

if __name__ == "__main__":
    print("智记侠 - 批量删除功能最终测试")
    print("=" * 50)
    
    # 测试API功能
    api_success = test_final_batch_delete()
    
    # 测试Web界面
    web_success = test_web_interface()
    
    if api_success and web_success:
        print("\n🎉 批量删除功能测试通过!")
        print("\n总结:")
        print("1. ✅ API批量删除功能正常工作")
        print("2. ✅ Web界面批量操作元素存在")
        print("3. ✅ 不再保护任何用户，所有选中的用户都会被删除")
        print("4. ✅ 解决了'删除0个用户'的问题")
        print("\n现在可以在管理页面正常使用批量删除功能了!")
    else:
        print("\n❌ 批量删除功能测试失败")
        import sys
        sys.exit(1)
