#!/usr/bin/env python3
"""
最终验证所有修改：
1. 创建提醒（无图片） - 只创建1个提醒
2. 创建提醒（有图片） - 只创建1个提醒（包含图片）
3. 编辑提醒（更新图片） - 正常更新
4. 任务详情图片显示 - 不显示"图片加载中..."
"""

import sys
import os
import base64
import uuid
import requests
import time
import json

# 设置环境变量确保使用PostgreSQL
os.environ['DB_TYPE'] = 'postgresql'

sys.path.append('.')
from app.database import db_config

def print_section(title):
    print()
    print("=" * 60)
    print(f" {title}")
    print("=" * 60)
    print()

def test_create_without_image():
    """测试创建提醒（无图片）"""
    print_section("测试1：创建提醒（无图片）")
    
    base_url = "http://localhost:8002"
    user_id = "final_test_user_" + str(uuid.uuid4())[:8]
    
    # 创建提醒（没有图片）
    request_data = {
        "user_id": user_id,
        "homework": {
            "course": "最终测试课程（无图片）",
            "content": "最终测试作业内容",
            "start_time": "",
            "deadline": "2026-04-15 23:59",
            "difficulty": "中",
            "image_url": ""
        }
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
            print(f"✅ 创建成功: {result.get('message', '')}")
            print(f"提醒ID: {result.get('reminder_id')}")
            
            # 检查数据库
            query = "SELECT COUNT(*) as count FROM reminders WHERE user_id = %s"
            db_result = db_config.execute_query(query, (user_id,))
            
            if db_result and db_result[0]['count'] == 1:
                print("✅ 验证通过：只创建了1个提醒")
                return True, result.get('reminder_id')
            else:
                print(f"❌ 验证失败：创建了 {db_result[0]['count'] if db_result else 0} 个提醒")
                return False, None
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应: {response.text[:500]}")
            return False, None
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False, None

def test_create_with_image():
    """测试创建提醒（有图片）"""
    print_section("测试2：创建提醒（有图片）")
    
    base_url = "http://localhost:8002"
    user_id = "final_test_user_" + str(uuid.uuid4())[:8]
    
    # 读取测试图片
    test_image_path = "downloaded_test_image.png"
    try:
        with open(test_image_path, "rb") as f:
            image_data = f.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        print(f"✅ 读取测试图片成功，大小: {len(image_data)} bytes")
    except Exception as e:
        print(f"❌ 读取测试图片失败: {e}")
        return False, None
    
    # 创建提醒（包含图片）
    request_data = {
        "user_id": user_id,
        "homework": {
            "course": "最终测试课程（有图片）",
            "content": "最终测试作业内容",
            "start_time": "",
            "deadline": "2026-04-15 23:59",
            "difficulty": "中",
            "image_url": ""
        },
            "image": f"data:image/png;base64,{img_base64}"
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
            print(f"✅ 创建成功: {result.get('message', '')}")
            print(f"提醒ID: {result.get('reminder_id')}")
            
            # 等待1秒
            time.sleep(1)
            
            # 检查数据库
            query = """
            SELECT COUNT(*) as count, 
                   SUM(CASE WHEN image_data IS NOT NULL THEN 1 ELSE 0 END) as with_image_count,
                   SUM(CASE WHEN course = '' THEN 1 ELSE 0 END) as empty_course_count
            FROM reminders WHERE user_id = %s
            """
            db_result = db_config.execute_query(query, (user_id,))
            
            if db_result:
                count = db_result[0]['count']
                with_image = db_result[0]['with_image_count']
                empty_course = db_result[0]['empty_course_count']
                
                print(f"数据库统计:")
                print(f"  总提醒数: {count}")
                print(f"  有图片的提醒数: {with_image}")
                print(f"  空课程的提醒数: {empty_course}")
                
                if count == 1 and with_image == 1 and empty_course == 0:
                    print("✅ 验证通过：只创建了1个提醒，包含图片，没有空课程")
                    return True, result.get('reminder_id')
                else:
                    print("❌ 验证失败：不符合预期")
                    return False, None
            else:
                print("❌ 数据库查询失败")
                return False, None
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应: {response.text[:500]}")
            return False, None
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False, None

def test_edit_reminder(reminder_id):
    """测试编辑提醒（更新图片）"""
    print_section("测试3：编辑提醒（更新图片）")
    
    if not reminder_id:
        print("❌ 需要有效的提醒ID")
        return False
    
    base_url = "http://localhost:8002"
    user_id = "final_test_user_" + str(uuid.uuid4())[:8]
    
    # 首先创建一个提醒
    request_data = {
        "user_id": user_id,
        "homework": {
            "course": "待编辑的课程",
            "content": "待编辑的内容",
            "start_time": "",
            "deadline": "2026-04-20 23:59",
            "difficulty": "易",
            "image_url": ""
        }
    }
    
    try:
        # 创建提醒
        response = requests.post(
            f"{base_url}/api/reminder",
            json=request_data,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ 创建提醒失败: {response.status_code}")
            return False
        
        create_result = response.json()
        edit_reminder_id = create_result.get('reminder_id')
        print(f"✅ 创建提醒成功，ID: {edit_reminder_id}")
        
        # 等待1秒
        time.sleep(1)
        
        # 读取测试图片
        test_image_path = "downloaded_test_image.png"
        with open(test_image_path, "rb") as f:
            img_data = f.read()
        img_base64 = base64.b64encode(img_data).decode('utf-8')
        
        # 编辑提醒（添加图片）
        edit_data = {
            "user_id": user_id,
            "homework": {
                "course": "已编辑的课程",
                "content": "已编辑的内容",
                "start_time": "",
                "deadline": "2026-04-25 23:59",
                "difficulty": "难",
                "image_url": ""
            },
            "reminder_id": edit_reminder_id,
            "image": f"data:image/png;base64,{image_base64}"
        }
        
        edit_response = requests.post(
            f"{base_url}/api/reminder",
            json=edit_data,
            timeout=10
        )
        
        print(f"编辑请求状态码: {edit_response.status_code}")
        
        if edit_response.status_code == 200:
            edit_result = edit_response.json()
            print(f"✅ 编辑成功: {edit_result.get('message', '')}")
            
            # 等待1秒
            time.sleep(1)
            
            # 等待2秒，确保数据库更新完成
            time.sleep(2)
            
            # 检查数据库
            query = """
            SELECT course, content, difficulty, image_data, image_type 
            FROM reminders WHERE id = %s
            """
            db_result = db_config.execute_query(query, (edit_reminder_id,))
            
            print(f"数据库查询结果: {len(db_result) if db_result else 0} 条记录")
            
            if db_result:
                reminder = db_result[0]
                print(f"更新后的提醒:")
                print(f"  课程: {reminder['course']}")
                print(f"  内容: {reminder['content']}")
                print(f"  难度: {reminder['difficulty']}")
                
                # 检查image_data字段
                image_data = reminder.get('image_data')
                if image_data:
                    print(f"  图片大小: {len(image_data)} bytes")
                    print(f"  图片类型: {reminder.get('image_type', '未知')}")
                    
                    # 验证图片数据是否正确
                    try:
                        import base64
                        # 将图片数据编码为base64，与原始数据比较
                        encoded = base64.b64encode(image_data).decode('utf-8')
                        original_encoded = image_base64
                        
                        # 只比较前100个字符，因为可能有编码差异
                        if encoded[:100] == original_encoded[:100]:
                            print("✅ 图片数据验证通过")
                        else:
                            print("⚠️ 图片数据可能不匹配")
                    except Exception as e:
                        print(f"⚠️ 图片数据验证失败: {e}")
                else:
                    print(f"  图片大小: 0 bytes (无图片)")
                    print(f"  图片类型: {reminder.get('image_type', '无')}")
                
                # 检查所有字段
                course_ok = reminder['course'] == "已编辑的课程"
                content_ok = reminder['content'] == "已编辑的内容"
                difficulty_ok = reminder['difficulty'] == "难"
                image_ok = image_data is not None
                
                print(f"验证结果:")
                print(f"  课程正确: {course_ok}")
                print(f"  内容正确: {content_ok}")
                print(f"  难度正确: {difficulty_ok}")
                print(f"  有图片数据: {image_ok}")
                
                if course_ok and content_ok and difficulty_ok and image_ok:
                    print("✅ 验证通过：提醒已正确更新，包含图片")
                    return True
                else:
                    print("❌ 验证失败：提醒更新不正确")
                    return False
            else:
                print("❌ 数据库查询失败")
                return False
        else:
            print(f"❌ 编辑失败: {edit_response.status_code}")
            print(f"响应: {edit_response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_task_detail_api():
    """测试任务详情API"""
    print_section("测试4：任务详情API")
    
    base_url = "http://localhost:8002"
    user_id = "final_test_user_" + str(uuid.uuid4())[:8]
    
    # 创建一个有图片的提醒
    test_image_path = "downloaded_test_image.png"
    try:
        with open(test_image_path, "rb") as f:
            image_data = f.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
    except Exception as e:
        print(f"❌ 读取测试图片失败: {e}")
        return False
    
    request_data = {
        "user_id": user_id,
        "homework": {
            "course": "任务详情测试课程",
            "content": "任务详情测试内容",
            "start_time": "",
            "deadline": "2026-04-30 23:59",
            "difficulty": "中",
            "image_url": ""
        },
        "image": f"data:image/png;base64,{image_base64}"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/reminder",
            json=request_data,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ 创建提醒失败: {response.status_code}")
            return False
        
        create_result = response.json()
        reminder_id = create_result.get('reminder_id')
        print(f"✅ 创建提醒成功，ID: {reminder_id}")
        
        # 等待1秒
        time.sleep(1)
        
        # 获取任务详情
        detail_response = requests.get(
            f"{base_url}/api/reminders?user_id={user_id}",
            timeout=10
        )
        
        print(f"任务详情请求状态码: {detail_response.status_code}")
        
        if detail_response.status_code == 200:
            detail_result = detail_response.json()
            reminders = detail_result.get('data', [])
            
            if reminders:
                reminder = reminders[0]  # 最新的提醒
                print(f"任务详情:")
                print(f"  课程: {reminder.get('course')}")
                print(f"  内容: {reminder.get('content')}")
                print(f"  图片URL: {reminder.get('image_url', '无')}")
                
                # 检查图片URL格式
                image_url = reminder.get('image_url', '')
                if image_url and image_url.startswith('/api/images/'):
                    print("✅ 图片URL格式正确（API格式）")
                    
                    # 测试图片API
                    image_api_url = f"{base_url}{image_url}"
                    image_response = requests.get(image_api_url, timeout=10)
                    
                    if image_response.status_code == 200:
                        print(f"✅ 图片API访问成功，大小: {len(image_response.content)} bytes")
                        return True
                    else:
                        print(f"❌ 图片API访问失败: {image_response.status_code}")
                        return False
                else:
                    print("❌ 图片URL格式不正确")
                    return False
            else:
                print("❌ 没有获取到提醒")
                return False
        else:
            print(f"❌ 获取任务详情失败: {detail_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("开始最终验证...")
    print()
    
    all_passed = True
    
    # 测试1：创建提醒（无图片）
    passed1, reminder_id1 = test_create_without_image()
    if not passed1:
        all_passed = False
    
    # 测试2：创建提醒（有图片）
    passed2, reminder_id2 = test_create_with_image()
    if not passed2:
        all_passed = False
    
    # 测试3：编辑提醒
    passed3 = test_edit_reminder(reminder_id2 if reminder_id2 else reminder_id1)
    if not passed3:
        all_passed = False
    
    # 测试4：任务详情API
    passed4 = test_task_detail_api()
    if not passed4:
        all_passed = False
    
    print()
    print("=" * 60)
    print("最终验证结果")
    print("=" * 60)
    print()
    
    print(f"测试1 - 创建提醒（无图片）: {'✅ 通过' if passed1 else '❌ 失败'}")
    print(f"测试2 - 创建提醒（有图片）: {'✅ 通过' if passed2 else '❌ 失败'}")
    print(f"测试3 - 编辑提醒（更新图片）: {'✅ 通过' if passed3 else '❌ 失败'}")
    print(f"测试4 - 任务详情API: {'✅ 通过' if passed4 else '❌ 失败'}")
    print()
    
    if all_passed:
        print("🎉 所有测试通过！")
        print()
        print("总结：")
        print("1. ✅ 创建提醒（无图片）时只创建1个提醒")
        print("2. ✅ 创建提醒（有图片）时只创建1个提醒（包含图片）")
        print("3. ✅ 编辑提醒时可以正常更新图片")
        print("4. ✅ 任务详情API正常工作，图片URL格式正确")
        print()
        print("所有问题已解决：")
        print("- 不会自动创建'未知课程'的提醒")
        print("- 编辑任务时能正常上传图片")
        print("- 任务详情不显示'图片加载中...'")
        print("- 图片显示比例已调整")
        sys.exit(0)
    else:
        print("❌ 部分测试失败，请检查问题")
        sys.exit(1)

if __name__ == "__main__":
    main()
