#!/usr/bin/env python3
"""
测试批量操作功能
"""

import os
os.environ['DB_TYPE'] = 'postgresql'

import uuid
import requests
import json

def test_batch_operations():
    """测试批量操作功能"""
    print("=== 测试批量操作功能 ===")
    
    base_url = "http://localhost:8004"
    
    # 1. 首先创建一些测试提醒
    print("1. 创建测试提醒...")
    test_reminder_ids = []
    user_id = "batch_test_user_" + str(uuid.uuid4())[:8]
    
    for i in range(3):
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
            result = response.json()
            reminder_id = result.get('reminder_id')
            test_reminder_ids.append(reminder_id)
            print(f"  创建提醒 {i+1} 成功: {reminder_id[:8]}...")
        else:
            print(f"  创建提醒 {i+1} 失败: {response.status_code}")
    
    if len(test_reminder_ids) < 2:
        print("❌ 创建测试提醒失败，无法继续测试")
        return False
    
    print(f"✅ 创建 {len(test_reminder_ids)} 个测试提醒成功")
    
    # 2. 测试批量完成
    print("\n2. 测试批量完成...")
    batch_complete_data = {
        "reminder_ids": test_reminder_ids[:2]  # 只完成前2个
    }
    
    response = requests.post(
        f"{base_url}/management/reminders/batch-complete",
        json=batch_complete_data,
        timeout=10
    )
    
    print(f"批量完成请求状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 批量完成成功: {result.get('message', '')}")
        print(f"   完成数量: {result.get('completed_count', 0)}")
    else:
        print(f"❌ 批量完成失败: {response.status_code}")
        print(f"   响应: {response.text[:500]}")
        return False
    
    # 3. 测试批量删除
    print("\n3. 测试批量删除...")
    batch_delete_data = {
        "reminder_ids": test_reminder_ids[2:]  # 删除第3个
    }
    
    response = requests.post(
        f"{base_url}/management/reminders/batch-delete",
        json=batch_delete_data,
        timeout=10
    )
    
    print(f"批量删除请求状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 批量删除成功: {result.get('message', '')}")
        print(f"   删除数量: {result.get('deleted_count', 0)}")
    else:
        print(f"❌ 批量删除失败: {response.status_code}")
        print(f"   响应: {response.text[:500]}")
        return False
    
    # 4. 验证结果
    print("\n4. 验证结果...")
    # 检查管理页面是否能正常访问
    response = requests.get(
        f"{base_url}/management/reminders",
        timeout=10
    )
    
    if response.status_code == 200:
        print("✅ 管理页面可正常访问")
    else:
        print(f"❌ 管理页面访问失败: {response.status_code}")
        return False
    
    print("\n" + "=" * 50)
    print("批量操作测试完成!")
    print("=" * 50)
    
    # 清理：删除所有测试提醒
    print("\n5. 清理测试数据...")
    for reminder_id in test_reminder_ids:
        # 尝试删除，即使可能已经被删除了
        try:
            delete_data = {
                "user_id": user_id,
                "reminder_id": reminder_id,
                "homework": {
                    "course": "清理",
                    "content": "清理",
                    "start_time": "",
                    "deadline": "2026-04-30 23:59",
                    "difficulty": "中",
                    "image_url": ""
                }
            }
            requests.post(f"{base_url}/api/reminder", json=delete_data, timeout=5)
        except:
            pass
    
    return True

if __name__ == "__main__":
    success = test_batch_operations()
    
    if success:
        print("\n🎉 批量操作功能测试通过!")
        print("\n现在可以访问管理页面查看批量操作功能:")
        print("1. 打开浏览器访问: http://localhost:8004/management/reminders")
        print("2. 选择提醒前的复选框")
        print("3. 使用批量完成、批量删除或批量导出按钮")
    else:
        print("\n❌ 批量操作功能测试失败")
        import sys
        sys.exit(1)
