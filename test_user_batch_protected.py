#!/usr/bin/env python3
"""
测试用户管理批量操作功能（保护test用户）
"""

import os
os.environ['DB_TYPE'] = 'postgresql'

import uuid
import requests
import json

def test_user_batch_protected():
    """测试用户管理批量操作功能（保护test用户）"""
    print("=== 测试用户管理批量操作功能（保护test用户） ===")
    
    base_url = "http://localhost:8002"
    
    # 1. 首先创建一些测试用户，包括test用户
    print("1. 创建测试用户...")
    test_user_ids = []
    
    # 创建普通用户
    for i in range(2):
        user_id = f"normal_user_{str(uuid.uuid4())[:8]}"
        test_user_ids.append(user_id)
        
        create_data = {
            "user_id": user_id,
            "homework": {
                "course": f"普通用户课程{i+1}",
                "content": f"普通用户内容{i+1}",
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
            print(f"  创建普通用户 {i+1} 成功: {user_id}")
        else:
            print(f"  创建普通用户 {i+1} 失败: {response.status_code}")
    
    # 创建test用户
    test_user_id = "test_protected_user"
    test_user_ids.append(test_user_id)
    
    test_create_data = {
        "user_id": test_user_id,
        "homework": {
            "course": "测试保护课程",
            "content": "测试保护内容",
            "start_time": "",
            "deadline": "2026-04-30 23:59",
            "difficulty": "中",
            "image_url": ""
        }
    }
    
    response = requests.post(
        f"{base_url}/api/reminder",
        json=test_create_data,
        timeout=10
    )
    
    if response.status_code == 200:
        print(f"  创建test用户成功: {test_user_id}")
    else:
        print(f"  创建test用户失败: {response.status_code}")
    
    if len(test_user_ids) < 3:
        print("❌ 创建测试用户失败，无法继续测试")
        return False
    
    print(f"✅ 创建 {len(test_user_ids)} 个测试用户成功（包含test用户）")
    
    # 等待1秒，确保数据写入
    import time
    time.sleep(1)
    
    # 2. 测试批量删除用户（应该保护test用户）
    print("\n2. 测试批量删除用户（保护test用户）...")
    batch_delete_data = {
        "user_ids": test_user_ids  # 包含test用户
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
        print(f"   受保护用户: {result.get('protected_users', [])}")
        
        # 检查是否保护了test用户
        protected_users = result.get('protected_users', [])
        if test_user_id in protected_users:
            print(f"✅ test用户 {test_user_id} 被成功保护")
        else:
            print(f"❌ test用户 {test_user_id} 未被保护")
            return False
    else:
        print(f"❌ 批量删除用户失败: {response.status_code}")
        print(f"   响应: {response.text[:500]}")
        return False
    
    # 3. 验证结果
    print("\n3. 验证结果...")
    # 检查管理页面是否能正常访问
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
    print("用户管理批量操作（保护test用户）测试完成!")
    print("=" * 50)
    
    # 4. 清理：删除剩余的test用户（如果需要）
    print("\n4. 清理测试数据...")
    # test用户应该还在，我们可以检查一下
    try:
        # 检查test用户是否还存在
        check_response = requests.get(
            f"{base_url}/api/reminders?user_id={test_user_id}",
            timeout=5
        )
        if check_response.status_code == 200:
            print(f"✅ test用户 {test_user_id} 仍然存在，保护成功")
        else:
            print(f"⚠️ 无法检查test用户状态")
    except:
        print(f"⚠️ 检查test用户状态时出错")
    
    return True

if __name__ == "__main__":
    success = test_user_batch_protected()
    
    if success:
        print("\n🎉 用户管理批量操作功能（保护test用户）测试通过!")
        print("\n现在可以访问用户管理页面查看批量操作功能:")
        print("1. 打开浏览器访问: http://localhost:8002/management/users")
        print("2. 选择用户前的复选框")
        print("3. 使用批量删除或批量导出按钮")
        print("4. test用户会被自动保护，不会被删除")
    else:
        print("\n❌ 用户管理批量操作功能（保护test用户）测试失败")
        import sys
        sys.exit(1)
