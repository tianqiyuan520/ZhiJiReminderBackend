#!/usr/bin/env python3
"""
测试新的保存流程：
1. 上传图片（创建包含"待填写课程"的提醒）
2. 使用返回的reminder_id更新提醒信息
3. 验证不会创建重复的提醒
"""

import sys
import os
import base64
import uuid
import requests
import json

# 设置环境变量确保使用PostgreSQL
os.environ['DB_TYPE'] = 'postgresql'

sys.path.append('.')
from app.database import db_config

def test_new_save_workflow():
    """测试新的保存流程"""
    print("=== 测试新的保存流程（避免重复创建'待填写课程'） ===")
    print()
    
    # 服务器地址
    base_url = "http://localhost:8002"
    
    # 1. 读取测试图片
    test_image_path = "downloaded_test_image.png"
    try:
        with open(test_image_path, "rb") as f:
            image_data = f.read()
        
        # 转换为base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        print(f"1. 读取测试图片成功")
        print(f"   图片大小: {len(image_data)} bytes")
        print()
    except FileNotFoundError:
        print(f"❌ 测试图片文件不存在: {test_image_path}")
        return False
    except Exception as e:
        print(f"❌ 读取测试图片失败: {e}")
        return False
    
    # 2. 上传图片（创建包含"待填写课程"的提醒）
    print("2. 上传图片（创建包含'待填写课程'的提醒）")
    
    user_id = "test_user_" + str(uuid.uuid4())[:8]  # 生成唯一的用户ID
    request_data = {
        "image": image_base64,
        "user_id": user_id
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/upload-image-only",
            json=request_data,
            timeout=30
        )
        
        print(f"   请求URL: {base_url}/api/upload-image-only")
        print(f"   用户ID: {user_id}")
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   响应成功: {result.get('success', False)}")
            
            if result.get('success'):
                data = result.get('data', {})
                reminder_id = data.get('reminder_id')
                image_url = data.get('image_url')
                
                print(f"   提醒ID: {reminder_id}")
                print(f"   图片URL: {image_url}")
                print()
                
                # 3. 验证数据库中的提醒
                print("3. 验证数据库中的提醒（应该是'待填写课程'）")
                
                query = """
                SELECT id, user_id, course, content, deadline, image_data
                FROM reminders 
                WHERE id = %s
                """
                
                db_result = db_config.execute_query(query, (reminder_id,))
                
                if db_result and len(db_result) > 0:
                    row = db_result[0]
                    print(f"   数据库查询成功:")
                    print(f"     ID: {row.get('id')}")
                    print(f"     用户: {row.get('user_id')}")
                    print(f"     课程: {row.get('course')}")
                    print(f"     内容: {row.get('content')}")
                    print(f"     截止时间: {row.get('deadline')}")
                    print(f"     图片大小: {len(row.get('image_data', b''))} bytes")
                    
                    if row.get('course') == "待填写课程":
                        print("   ✅ 提醒包含默认的'待填写课程'（正确）")
                    else:
                        print(f"   ⚠️ 课程不是'待填写课程': {row.get('course')}")
                else:
                    print("   ❌ 数据库中没有找到该记录")
                    return False
                
                print()
                
                # 4. 使用reminder_id更新提醒信息
                print("4. 使用reminder_id更新提醒信息（应该更新而不是创建新提醒）")
                
                update_data = {
                    "user_id": user_id,
                    "homework": {
                        "course": "测试课程",
                        "content": "测试作业内容",
                        "start_time": "",
                        "deadline": "2026-04-10 23:59",
                        "difficulty": "中",
                        "image_url": image_url
                    },
                    "reminder_id": reminder_id  # 关键：提供reminder_id
                }
                
                update_response = requests.post(
                    f"{base_url}/api/reminder",
                    json=update_data,
                    timeout=30
                )
                
                print(f"   请求URL: {base_url}/api/reminder")
                print(f"   状态码: {update_response.status_code}")
                
                if update_response.status_code == 200:
                    update_result = update_response.json()
                    print(f"   响应成功: {update_result.get('success', False)}")
                    print(f"   消息: {update_result.get('message', '')}")
                    
                    returned_reminder_id = update_result.get('reminder_id')
                    print(f"   返回的提醒ID: {returned_reminder_id}")
                    
                    if returned_reminder_id == reminder_id:
                        print("   ✅ 返回的提醒ID与原始ID相同（更新成功）")
                    else:
                        print(f"   ⚠️ 返回的提醒ID不同: {returned_reminder_id}")
                else:
                    print(f"   请求失败: {update_response.status_code}")
                    print(f"   响应: {update_response.text[:500]}")
                    return False
                
                print()
                
                # 5. 验证更新后的提醒
                print("5. 验证更新后的提醒")
                
                # 查询数据库
                verify_query = """
                SELECT id, user_id, course, content, deadline, image_data
                FROM reminders 
                WHERE user_id = %s
                ORDER BY created_at DESC
                """
                
                verify_result = db_config.execute_query(verify_query, (user_id,))
                
                if verify_result and len(verify_result) > 0:
                    print(f"   用户 {user_id} 有 {len(verify_result)} 条提醒")
                    
                    # 显示所有提醒
                    for i, row in enumerate(verify_result):
                        print(f"   提醒 {i+1}:")
                        print(f"     ID: {row.get('id')}")
                        print(f"     课程: {row.get('course')}")
                        print(f"     内容: {row.get('content')}")
                        print(f"     截止时间: {row.get('deadline')}")
                    
                    # 检查是否有重复的"待填写课程"
                    pending_courses = [r.get('course') for r in verify_result if r.get('course') == "待填写课程"]
                    if len(pending_courses) > 1:
                        print(f"   ❌ 发现 {len(pending_courses)} 个'待填写课程'（有重复）")
                        return False
                    elif len(pending_courses) == 1:
                        # 检查这个"待填写课程"是否是我们刚刚更新的那个
                        pending_reminder = [r for r in verify_result if r.get('course') == "待填写课程"][0]
                        if pending_reminder.get('id') == reminder_id:
                            print("   ❌ 提醒仍然是'待填写课程'（更新失败）")
                            return False
                        else:
                            print("   ❌ 有另一个'待填写课程'提醒")
                            return False
                    else:
                        print("   ✅ 没有重复的'待填写课程'提醒")
                    
                    # 检查我们的提醒是否已更新
                    updated_reminder = [r for r in verify_result if r.get('id') == reminder_id]
                    if updated_reminder:
                        if updated_reminder[0].get('course') == "测试课程":
                            print("   ✅ 提醒已成功更新为'测试课程'")
                        else:
                            print(f"   ❌ 提醒课程未更新: {updated_reminder[0].get('course')}")
                            return False
                    else:
                        print("   ❌ 找不到更新后的提醒")
                        return False
                else:
                    print("   ❌ 用户没有提醒")
                    return False
                
                print()
                print("=== 测试总结 ===")
                print("✅ 新的保存流程测试通过！")
                print(f"   1. 上传图片创建了提醒: {reminder_id}")
                print(f"   2. 使用reminder_id更新了提醒信息")
                print(f"   3. 没有创建重复的'待填写课程'提醒")
                print(f"   4. 提醒已成功更新为'测试课程'")
                
                return True
            else:
                print(f"   上传失败: {result.get('message', '未知错误')}")
                return False
        else:
            print(f"   请求失败: {response.status_code}")
            print(f"   响应: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_new_save_workflow()
    if success:
        print("\n🎉 测试成功！新的保存流程避免了重复创建'待填写课程'的问题。")
        print("   前端现在应该：")
        print("   1. 上传图片时调用 /api/upload-image-only")
        print("   2. 保存提醒时调用 /api/reminder 并传递 reminder_id")
        print("   3. 这样就不会创建重复的提醒了")
    else:
        print("\n❌ 测试失败！请检查错误信息。")
    
    sys.exit(0 if success else 1)
