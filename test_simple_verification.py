#!/usr/bin/env python3
"""
简化验证核心功能：
1. 创建提醒（有图片） - 只创建1个提醒
2. 编辑提醒（更新图片） - 正常更新
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

def test_create_with_image():
    """测试创建提醒（有图片）"""
    print("=== 测试1：创建提醒（有图片） ===")
    
    base_url = "http://localhost:8003"
    user_id = "simple_test_user_" + str(uuid.uuid4())[:8]
    
    # 读取测试图片
    test_image_path = "downloaded_test_image.png"
    try:
        with open(test_image_path, "rb") as f:
            image_data = f.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        print(f"读取测试图片成功，大小: {len(image_data)} bytes")
    except Exception as e:
        print(f"❌ 读取测试图片失败: {e}")
        return False, None
    
    # 创建提醒（包含图片）
    request_data = {
        "user_id": user_id,
        "homework": {
            "course": "简单测试课程",
            "content": "简单测试内容",
            "start_time": "",
            "deadline": "2026-04-15 23:59",
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
        
        print(f"请求状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 创建成功: {result.get('message', '')}")
            reminder_id = result.get('reminder_id')
            print(f"提醒ID: {reminder_id}")
            
            # 等待1秒
            time.sleep(1)
            
            # 检查数据库
            query = "SELECT COUNT(*) as count FROM reminders WHERE user_id = %s"
            db_result = db_config.execute_query(query, (user_id,))
            
            if db_result and db_result[0]['count'] == 1:
                print("✅ 验证通过：只创建了1个提醒")
                return True, reminder_id
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

def test_edit_reminder_simple(reminder_id):
    """测试编辑提醒（更新图片）- 简化版本"""
    print("\n=== 测试2：编辑提醒（更新图片） ===")
    
    if not reminder_id:
        print("❌ 需要有效的提醒ID")
        return False
    
    base_url = "http://localhost:8003"
    user_id = "simple_test_user_" + str(uuid.uuid4())[:8]
    
    # 首先创建一个提醒（无图片）
    request_data = {
        "user_id": user_id,
        "homework": {
            "course": "待编辑课程",
            "content": "待编辑内容",
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
                "course": "已编辑课程",
                "content": "已编辑内容",
                "start_time": "",
                "deadline": "2026-04-25 23:59",
                "difficulty": "难",
                "image_url": ""
            },
            "reminder_id": edit_reminder_id,
            "image": f"data:image/png;base64,{img_base64}"
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
            
            # 等待2秒，确保数据库更新完成
            time.sleep(2)
            
            # 检查数据库
            query = """
            SELECT course, content, difficulty, image_data 
            FROM reminders WHERE id = %s
            """
            db_result = db_config.execute_query(query, (edit_reminder_id,))
            
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
                    print("✅ 验证通过：提醒已正确更新，包含图片")
                    return True
                else:
                    print(f"  图片大小: 0 bytes (无图片)")
                    print("❌ 验证失败：提醒更新后没有图片数据")
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

def main():
    print("开始简化验证...")
    print()
    
    # 测试1：创建提醒（有图片）
    passed1, reminder_id = test_create_with_image()
    
    if not passed1:
        print("\n❌ 测试1失败，跳过测试2")
        sys.exit(1)
    
    # 测试2：编辑提醒
    passed2 = test_edit_reminder_simple(reminder_id)
    
    print()
    print("=" * 50)
    print("简化验证结果")
    print("=" * 50)
    print()
    
    print(f"测试1 - 创建提醒（有图片）: {'✅ 通过' if passed1 else '❌ 失败'}")
    print(f"测试2 - 编辑提醒（更新图片）: {'✅ 通过' if passed2 else '❌ 失败'}")
    print()
    
    if passed1 and passed2:
        print("🎉 核心功能验证通过！")
        print()
        print("总结：")
        print("1. ✅ 创建提醒（有图片）时只创建1个提醒")
        print("2. ✅ 编辑提醒时可以正常更新图片")
        print()
        print("核心问题已解决：")
        print("- 不会自动创建'未知课程'的提醒")
        print("- 编辑任务时能正常上传图片")
        sys.exit(0)
    else:
        print("❌ 核心功能验证失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
