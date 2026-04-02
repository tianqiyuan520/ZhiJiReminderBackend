#!/usr/bin/env python3
"""
测试重复触发创建提醒的情况
模拟前端可能的行为：
1. 快速连续调用API
2. 一个操作触发多个API调用
"""

import sys
import os
import base64
import uuid
import requests
import json
import threading
import time

# 设置环境变量确保使用PostgreSQL
os.environ['DB_TYPE'] = 'postgresql'

sys.path.append('.')
from app.database import db_config

def test_rapid_api_calls():
    """测试快速连续调用API（模拟重复触发）"""
    print("=== 测试快速连续调用API（模拟重复触发） ===")
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
    
    # 模拟前端可能的行为：快速连续调用多个API
    print("模拟前端行为：快速连续调用多个API")
    print("1. 调用 /api/upload-image-only（上传图片）")
    print("2. 调用 /api/reminder（保存提醒）")
    print("3. 可能还有其他调用...")
    print()
    
    # 记录开始时间
    start_time = time.time()
    
    # 线程函数：调用API
    def call_upload_image_only():
        try:
            request_data = {
                "image": image_base64,
                "user_id": user_id
            }
            response = requests.post(
                f"{base_url}/api/upload-image-only",
                json=request_data,
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result.get('data', {}).get('reminder_id')
        except Exception as e:
            print(f"  上传图片失败: {e}")
        return None
    
    def call_reminder(reminder_id=None):
        try:
            request_data = {
                "user_id": user_id,
                "homework": {
                    "course": "测试课程",
                    "content": "测试作业内容",
                    "start_time": "",
                    "deadline": "2026-04-10 23:59",
                    "difficulty": "中",
                    "image_url": ""
                }
            }
            if reminder_id:
                request_data["reminder_id"] = reminder_id
            
            response = requests.post(
                f"{base_url}/api/reminder",
                json=request_data,
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result.get('reminder_id')
        except Exception as e:
            print(f"  保存提醒失败: {e}")
        return None
    
    # 模拟快速连续调用
    print("开始模拟快速连续调用...")
    
    # 场景1：先上传图片，然后保存提醒（正常流程）
    print("场景1：正常流程（先上传图片，然后保存提醒）")
    reminder_id1 = call_upload_image_only()
    if reminder_id1:
        print(f"  上传图片成功，获取reminder_id: {reminder_id1}")
        reminder_id2 = call_reminder(reminder_id1)
        if reminder_id2:
            print(f"  保存提醒成功，返回reminder_id: {reminder_id2}")
            if reminder_id1 == reminder_id2:
                print("  ✅ 两个reminder_id相同（更新成功）")
            else:
                print(f"  ⚠️ 两个reminder_id不同: {reminder_id1} vs {reminder_id2}")
    else:
        print("  ❌ 上传图片失败")
    
    print()
    
    # 场景2：快速连续调用两次保存提醒（模拟重复点击）
    print("场景2：快速连续调用两次保存提醒（模拟重复点击）")
    user_id2 = "test_user_" + str(uuid.uuid4())[:8]
    
    # 第一次调用
    request_data = {
        "user_id": user_id2,
        "homework": {
            "course": "测试课程2",
            "content": "测试内容2",
            "start_time": "",
            "deadline": "2026-04-11 23:59",
            "difficulty": "中",
            "image_url": ""
        },
        "image": f"data:image/png;base64,{image_base64}"
    }
    
    response1 = requests.post(f"{base_url}/api/reminder", json=request_data, timeout=10)
    response2 = requests.post(f"{base_url}/api/reminder", json=request_data, timeout=10)
    
    print(f"  第一次调用状态码: {response1.status_code}")
    print(f"  第二次调用状态码: {response2.status_code}")
    
    if response1.status_code == 200 and response2.status_code == 200:
        result1 = response1.json()
        result2 = response2.json()
        
        reminder_id1 = result1.get('reminder_id')
        reminder_id2 = result2.get('reminder_id')
        
        print(f"  第一次调用返回reminder_id: {reminder_id1}")
        print(f"  第二次调用返回reminder_id: {reminder_id2}")
        
        if reminder_id1 == reminder_id2:
            print("  ⚠️ 两个reminder_id相同（可能是幂等性问题）")
        else:
            print("  ❌ 两个reminder_id不同（创建了两个提醒）")
    
    print()
    
    # 检查数据库中的提醒数量
    print("检查数据库中的提醒数量...")
    
    query = """
    SELECT id, user_id, course, content, deadline, image_data
    FROM reminders 
    WHERE user_id IN (%s, %s)
    ORDER BY user_id, created_at DESC
    """
    
    db_result = db_config.execute_query(query, (user_id, user_id2))
    
    if db_result:
        print(f"找到 {len(db_result)} 条提醒:")
        
        # 按用户分组
        reminders_by_user = {}
        for row in db_result:
            user = row.get('user_id')
            if user not in reminders_by_user:
                reminders_by_user[user] = []
            reminders_by_user[user].append(row)
        
        for user, reminders in reminders_by_user.items():
            print(f"  用户 {user}: {len(reminders)} 条提醒")
            for i, reminder in enumerate(reminders):
                print(f"    提醒 {i+1}: ID={reminder.get('id')}, 课程={reminder.get('course')}, 图片大小={len(reminder.get('image_data', b''))} bytes")
            
            if len(reminders) > 1:
                print(f"  ❌ 用户 {user} 有 {len(reminders)} 条提醒（应该有1条）")
                
                # 检查是否有空课程的提醒
                empty_courses = [r for r in reminders if r.get('course') == ""]
                if empty_courses:
                    print(f"    其中有 {len(empty_courses)} 个空课程的提醒")
                
                # 检查是否有"未知课程"的提醒
                unknown_courses = [r for r in reminders if r.get('course') == "未知课程"]
                if unknown_courses:
                    print(f"    其中有 {len(unknown_courses)} 个'未知课程'的提醒")
            else:
                print(f"  ✅ 用户 {user} 只有1条提醒（正确）")
    else:
        print("  没有找到提醒")
    
    print()
    print(f"测试完成，总耗时: {time.time() - start_time:.2f}秒")
    
    return True

def check_existing_duplicates():
    """检查数据库中现有的重复提醒"""
    print("=== 检查数据库中现有的重复提醒 ===")
    print()
    
    # 查询所有用户的提醒数量
    query = """
    SELECT user_id, COUNT(*) as count, 
           SUM(CASE WHEN course = '' THEN 1 ELSE 0 END) as empty_course_count,
           SUM(CASE WHEN course = '未知课程' THEN 1 ELSE 0 END) as unknown_course_count,
           SUM(CASE WHEN course = '待填写课程' THEN 1 ELSE 0 END) as pending_course_count
    FROM reminders 
    GROUP BY user_id
    HAVING COUNT(*) > 1
    ORDER BY count DESC
    """
    
    db_result = db_config.execute_query(query)
    
    if db_result:
        print(f"找到 {len(db_result)} 个用户有重复提醒:")
        print()
        
        for row in db_result:
            user_id = row.get('user_id')
            count = row.get('count', 0)
            empty_count = row.get('empty_course_count', 0)
            unknown_count = row.get('unknown_course_count', 0)
            pending_count = row.get('pending_course_count', 0)
            
            print(f"用户: {user_id}")
            print(f"  总提醒数: {count}")
            print(f"  空课程提醒: {empty_count}")
            print(f"  '未知课程'提醒: {unknown_count}")
            print(f"  '待填写课程'提醒: {pending_count}")
            
            # 查询该用户的具体提醒
            detail_query = """
            SELECT id, course, content, deadline, created_at, 
                   LENGTH(image_data) as image_size
            FROM reminders 
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 5
            """
            
            details = db_config.execute_query(detail_query, (user_id,))
            
            if details:
                print("  最近提醒:")
                for i, detail in enumerate(details):
                    course = detail.get('course', '')
                    if course == "":
                        course = "[空课程]"
                    print(f"    {i+1}. ID: {detail.get('id')[:8]}..., 课程: {course}, 内容: {detail.get('content')[:20]}..., 图片大小: {detail.get('image_size', 0)} bytes, 创建时间: {detail.get('created_at')}")
            
            print()
    else:
        print("没有找到有重复提醒的用户")
    
    return True

if __name__ == "__main__":
    print("开始测试重复触发创建提醒的情况...")
    print()
    
    # 检查现有的重复提醒
    check_existing_duplicates()
    
    print("-" * 50)
    print()
    
    # 测试快速连续调用API
    test_rapid_api_calls()
    
    print()
    print("测试完成！")
    print()
    print("分析：")
    print("1. 如果前端快速连续调用API，可能会创建重复的提醒")
    print("2. 解决方案：")
    print("   - 前端：添加防重复点击机制（按钮禁用、loading状态）")
    print("   - 后端：添加幂等性处理（相同请求只处理一次）")
    print("   - 使用合并的API：/api/reminder 同时上传图片和保存提醒")
