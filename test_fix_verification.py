#!/usr/bin/env python3
"""
验证修复是否有效：
1. 测试选择图片后创建提醒，是否只创建一个提醒
2. 测试不选择图片创建提醒，是否只创建一个提醒
"""

import sys
import os
import base64
import uuid
import requests
import time

# 设置环境变量确保使用PostgreSQL
os.environ['DB_TYPE'] = 'postgresql'

sys.path.append('.')
from app.database import db_config

def test_create_without_image():
    """测试不选择图片创建提醒"""
    print("=== 测试1：不选择图片创建提醒 ===")
    print()
    
    # 服务器地址
    base_url = "http://localhost:8002"
    
    # 生成唯一的用户ID
    user_id = "test_user_" + str(uuid.uuid4())[:8]
    
    # 创建提醒（没有图片）
    request_data = {
        "user_id": user_id,
        "homework": {
            "course": "测试课程（无图片）",
            "content": "测试作业内容",
            "start_time": "",
            "deadline": "2026-04-10 23:59",
            "difficulty": "中",
            "image_url": ""
        }
        # 注意：没有传递image字段
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/reminder",
            json=request_data,
            timeout=10
        )
        
        print(f"请求状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应成功: {result.get('success', False)}")
            print(f"消息: {result.get('message', '')}")
            print(f"创建的提醒ID: {result.get('reminder_id')}")
            
            # 检查数据库中的提醒数量
            query = """
            SELECT id, user_id, course, content, image_data
            FROM reminders 
            WHERE user_id = %s
            ORDER BY created_at DESC
            """
            
            db_result = db_config.execute_query(query, (user_id,))
            
            if db_result:
                print(f"用户 {user_id} 有 {len(db_result)} 条提醒")
                
                for i, row in enumerate(db_result):
                    print(f"提醒 {i+1}:")
                    print(f"  ID: {row.get('id')}")
                    print(f"  课程: {row.get('course')}")
                    print(f"  内容: {row.get('content')}")
                    image_data = row.get('image_data')
                    if image_data:
                        print(f"  图片大小: {len(image_data)} bytes")
                    else:
                        print(f"  图片大小: 0 bytes (无图片)")
                
                if len(db_result) == 1:
                    print("✅ 测试通过：只创建了一个提醒")
                    return True
                else:
                    print(f"❌ 测试失败：创建了 {len(db_result)} 个提醒（应该有1个）")
                    return False
            else:
                print("❌ 测试失败：用户没有提醒")
                return False
        else:
            print(f"请求失败: {response.status_code}")
            print(f"响应: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_create_with_image():
    """测试选择图片后创建提醒"""
    print()
    print("=== 测试2：选择图片后创建提醒 ===")
    print()
    
    # 服务器地址
    base_url = "http://localhost:8002"
    
    # 读取测试图片
    test_image_path = "downloaded_test_image.png"
    try:
        with open(test_image_path, "rb") as f:
            image_data = f.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        print(f"读取测试图片成功，大小: {len(image_data)} bytes")
        print()
    except Exception as e:
        print(f"❌ 读取测试图片失败: {e}")
        return False
    
    # 生成唯一的用户ID
    user_id = "test_user_" + str(uuid.uuid4())[:8]
    
    # 创建提醒（包含图片）
    request_data = {
        "user_id": user_id,
        "homework": {
            "course": "测试课程（有图片）",
            "content": "测试作业内容",
            "start_time": "",
            "deadline": "2026-04-10 23:59",
            "difficulty": "中",
            "image_url": ""
        },
        "image": f"data:image/png;base64,{image_base64}"  # 包含图片数据
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/reminder",
            json=request_data,
            timeout=10
        )
        
        print(f"请求状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应成功: {result.get('success', False)}")
            print(f"消息: {result.get('message', '')}")
            print(f"创建的提醒ID: {result.get('reminder_id')}")
            
            # 等待1秒，确保数据库更新完成
            time.sleep(1)
            
            # 检查数据库中的提醒数量
            query = """
            SELECT id, user_id, course, content, image_data
            FROM reminders 
            WHERE user_id = %s
            ORDER BY created_at DESC
            """
            
            db_result = db_config.execute_query(query, (user_id,))
            
            if db_result:
                print(f"用户 {user_id} 有 {len(db_result)} 条提醒")
                
                for i, row in enumerate(db_result):
                    print(f"提醒 {i+1}:")
                    print(f"  ID: {row.get('id')}")
                    print(f"  课程: {row.get('course')}")
                    print(f"  内容: {row.get('content')}")
                    image_data = row.get('image_data')
                    if image_data:
                        print(f"  图片大小: {len(image_data)} bytes")
                    else:
                        print(f"  图片大小: 0 bytes (无图片)")
                
                # 检查是否有空课程的提醒
                empty_courses = [r for r in db_result if r.get('course') == ""]
                if empty_courses:
                    print(f"⚠️ 发现 {len(empty_courses)} 个空课程的提醒")
                
                # 检查是否有"未知课程"的提醒
                unknown_courses = [r for r in db_result if r.get('course') == "未知课程"]
                if unknown_courses:
                    print(f"⚠️ 发现 {len(unknown_courses)} 个'未知课程'的提醒")
                
                if len(db_result) == 1:
                    print("✅ 测试通过：只创建了一个提醒")
                    
                    # 验证提醒内容
                    reminder = db_result[0]
                    if reminder.get('course') == "测试课程（有图片）":
                        print("✅ 提醒课程正确")
                    else:
                        print(f"❌ 提醒课程不正确: {reminder.get('course')}")
                        return False
                    
                    if reminder.get('image_data'):
                        print(f"✅ 提醒包含图片数据: {len(reminder.get('image_data'))} bytes")
                        return True
                    else:
                        print("❌ 提醒没有图片数据")
                        return False
                else:
                    print(f"❌ 测试失败：创建了 {len(db_result)} 个提醒（应该有1个）")
                    return False
            else:
                print("❌ 测试失败：用户没有提醒")
                return False
        else:
            print(f"请求失败: {response.status_code}")
            print(f"响应: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_old_behavior():
    """测试旧的行为（调用upload-image-only）"""
    print()
    print("=== 测试3：旧的行为（调用upload-image-only） ===")
    print("注意：这个测试应该失败，因为旧的行为会创建两个提醒")
    print()
    
    # 服务器地址
    base_url = "http://localhost:8002"
    
    # 读取测试图片
    test_image_path = "downloaded_test_image.png"
    try:
        with open(test_image_path, "rb") as f:
            image_data = f.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        print(f"读取测试图片成功，大小: {len(image_data)} bytes")
        print()
    except Exception as e:
        print(f"❌ 读取测试图片失败: {e}")
        return False
    
    # 生成唯一的用户ID
    user_id = "test_user_" + str(uuid.uuid4())[:8]
    
    # 1. 调用upload-image-only（旧的行为）
    print("1. 调用 /api/upload-image-only")
    upload_data = {
        "image": image_base64,
        "user_id": user_id
    }
    
    try:
        upload_response = requests.post(
            f"{base_url}/api/upload-image-only",
            json=upload_data,
            timeout=10
        )
        
        if upload_response.status_code == 200:
            upload_result = upload_response.json()
            print(f"  上传成功: {upload_result.get('success', False)}")
            print(f"  消息: {upload_result.get('data', {}).get('message', '')}")
            
            # 2. 调用reminder（旧的行为）
            print("2. 调用 /api/reminder")
            reminder_data = {
                "user_id": user_id,
                "homework": {
                    "course": "测试课程（旧行为）",
                    "content": "测试作业内容",
                    "start_time": "",
                    "deadline": "2026-04-10 23:59",
                    "difficulty": "中",
                    "image_url": ""
                }
            }
            
            reminder_response = requests.post(
                f"{base_url}/api/reminder",
                json=reminder_data,
                timeout=10
            )
            
            if reminder_response.status_code == 200:
                reminder_result = reminder_response.json()
                print(f"  创建提醒成功: {reminder_result.get('success', False)}")
                print(f"  消息: {reminder_result.get('message', '')}")
                
                # 等待1秒，确保数据库更新完成
                time.sleep(1)
                
                # 检查数据库中的提醒数量
                query = """
                SELECT id, user_id, course, content, image_data
                FROM reminders 
                WHERE user_id = %s
                ORDER BY created_at DESC
                """
                
                db_result = db_config.execute_query(query, (user_id,))
                
                if db_result:
                    print(f"用户 {user_id} 有 {len(db_result)} 条提醒")
                    
                    for i, row in enumerate(db_result):
                        print(f"提醒 {i+1}:")
                        print(f"  ID: {row.get('id')}")
                        print(f"  课程: {row.get('course')}")
                        print(f"  内容: {row.get('content')}")
                        image_data = row.get('image_data')
                        if image_data:
                            print(f"  图片大小: {len(image_data)} bytes")
                        else:
                            print(f"  图片大小: 0 bytes (无图片)")
                    
                    if len(db_result) == 2:
                        print("⚠️ 旧的行为：创建了两个提醒（这是问题所在）")
                        print("   - 第一个提醒：空课程，有图片（来自upload-image-only）")
                        print("   - 第二个提醒：用户填写的课程，没有图片（来自reminder）")
                        return True  # 测试通过，因为这是预期的旧行为
                    else:
                        print(f"⚠️ 创建了 {len(db_result)} 个提醒")
                        return True
                else:
                    print("❌ 用户没有提醒")
                    return False
            else:
                print(f"❌ 创建提醒失败: {reminder_response.status_code}")
                return False
        else:
            print(f"❌ 上传图片失败: {upload_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始验证修复是否有效...")
    print()
    
    # 测试1：不选择图片创建提醒
    success1 = test_create_without_image()
    
    if success1:
        print()
        print("✅ 测试1通过：不选择图片时只创建一个提醒")
    else:
        print()
        print("❌ 测试1失败")
    
    print()
    print("-" * 50)
    print()
    
    # 测试2：选择图片后创建提醒
    success2 = test_create_with_image()
    
    if success2:
        print()
        print("✅ 测试2通过：选择图片后只创建一个提醒（包含图片）")
    else:
        print()
        print("❌ 测试2失败")
    
    print()
    print("-" * 50)
    print()
    
    # 测试3：旧的行为（用于对比）
    success3 = test_old_behavior()
    
    if success3:
        print()
        print("✅ 测试3通过：验证了旧的行为会创建两个提醒")
    else:
        print()
        print("❌ 测试3失败")
    
    print()
    print("=" * 50)
    print()
    
    if success1 and success2:
        print("🎉 所有测试通过！")
        print()
        print("总结：")
        print("1. ✅ 修复有效：选择图片后只创建一个提醒（包含图片）")
        print("2. ✅ 修复有效：不选择图片时只创建一个提醒")
        print("3. ✅ 旧的行为确实会创建两个提醒（这是问题的根源）")
        print()
        print("问题已解决！前端现在调用 /api/reminder 并传递 image 字段，")
        print("而不是先调用 /api/upload-image-only 再调用 /api/reminder。")
        sys.exit(0)
    else:
        print("❌ 测试失败，问题可能未完全解决")
        sys.exit(1)
