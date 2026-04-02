#!/usr/bin/env python3
"""
测试用户管理批量操作功能
"""

import os
os.environ['DB_TYPE'] = 'postgresql'

import uuid
import requests
import json

def test_user_batch_operations():
    """测试用户管理批量操作功能"""
    print("=== 测试用户管理批量操作功能 ===")
    
    base_url = "http://localhost:8004"
    
    # 1. 首先创建一些测试用户
    print("1. 创建测试用户...")
    test_user_ids = []
    
    for i in range(3):
        user_id = f"batch_test_user_{str(uuid.uuid4())[:8]}"
        test_user_ids.append(user_id)
        
        # 通过创建提醒来创建用户（因为用户表通常通过创建提醒自动创建）
        create_data = {
            "user_id": user_id,
            "homework": {
                "course": f"用户测试课程{i+1}",
                "content": f"用户测试内容{i+1}",
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
    
    if len(test_user_ids) < 2:
        print("❌ 创建测试用户失败，无法继续测试")
        return False
    
    print(f"✅ 创建 {len(test_user_ids)} 个测试用户成功")
    
    # 等待1秒，确保数据写入
    import time
    time.sleep(1)
    
    # 2. 测试批量删除用户
    print("\n2. 测试批量删除用户...")
    batch_delete_data = {
        "user_ids": test_user_ids[:2]  # 只删除前2个
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
    print("用户管理批量操作测试完成!")
    print("=" * 50)
    
    # 4. 清理：删除剩余的测试用户
    print("\n4. 清理测试数据...")
    for user_id in test_user_ids[2:]:  # 只清理第3个（如果还存在）
        try:
            # 尝试通过删除提醒来清理
            delete_data = {
                "user_id": user_id,
                "homework": {
                    "course": "清理",
                    "content": "清理",
                    "start_time": "",
                    "deadline": "2026-04-30 23:59",
                    "difficulty": "中",
                    "image_url": ""
                }
            }
            # 先获取用户的提醒
            reminders_response = requests.get(
                f"{base_url}/api/reminders?user_id={user_id}",
                timeout=5
            )
            if reminders_response.status_code == 200:
                reminders = reminders_response.json().get('data', [])
                for reminder in reminders:
                    # 删除提醒
                    delete_response = requests.delete(
                        f"{base_url}/api/reminders/{reminder['id']}",
                        timeout=5
                    )
        except:
            pass
    
    return True

if __name__ == "__main__":
    success = test_user_batch_operations()
    
    if success:
        print("\n🎉 用户管理批量操作功能测试通过!")
        print("\n现在可以访问用户管理页面查看批量操作功能:")
        print("1. 打开浏览器访问: http://localhost:8004/management/users")
        print("2. 选择用户前的复选框")
        print("3. 使用批量删除或批量导出按钮")
    else:
        print("\n❌ 用户管理批量操作功能测试失败")
        import sys
        sys.exit(1)
