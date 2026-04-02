#!/usr/bin/env python3
"""
直接测试更新提醒功能
"""

import os
os.environ['DB_TYPE'] = 'postgresql'
os.environ['LOG_LEVEL'] = 'DEBUG'  # 设置DEBUG级别以获取更多日志

import base64
import uuid
import requests
import time

def test_direct_update():
    """直接测试更新提醒"""
    print("=== 直接测试更新提醒 ===")
    
    base_url = "http://localhost:8003"
    user_id = "direct_test_user_" + str(uuid.uuid4())[:8]
    
    # 1. 首先创建一个提醒（无图片）
    print("1. 创建提醒（无图片）...")
    create_data = {
        "user_id": user_id,
        "homework": {
            "course": "待更新课程",
            "content": "待更新内容",
            "start_time": "",
            "deadline": "2026-04-20 23:59",
            "difficulty": "易",
            "image_url": ""
        }
    }
    
    create_response = requests.post(
        f"{base_url}/api/reminder",
        json=create_data,
        timeout=10
    )
    
    if create_response.status_code != 200:
        print(f"❌ 创建提醒失败: {create_response.status_code}")
        print(f"响应: {create_response.text[:500]}")
        return False
    
    create_result = create_response.json()
    reminder_id = create_result.get('reminder_id')
    print(f"✅ 创建提醒成功，ID: {reminder_id}")
    
    # 等待1秒
    time.sleep(1)
    
    # 2. 读取测试图片
    print("\n2. 读取测试图片...")
    test_image_path = "downloaded_test_image.png"
    try:
        with open(test_image_path, "rb") as f:
            image_data = f.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        print(f"✅ 读取测试图片成功，大小: {len(image_data)} bytes")
    except Exception as e:
        print(f"❌ 读取测试图片失败: {e}")
        return False
    
    # 3. 更新提醒（添加图片）
    print("\n3. 更新提醒（添加图片）...")
    update_data = {
        "user_id": user_id,
        "homework": {
            "course": "已更新课程",
            "content": "已更新内容",
            "start_time": "",
            "deadline": "2026-04-25 23:59",
            "difficulty": "难",
            "image_url": ""
        },
        "reminder_id": reminder_id,
        "image": f"data:image/png;base64,{image_base64}"
    }
    
    update_response = requests.post(
        f"{base_url}/api/reminder",
        json=update_data,
        timeout=10
    )
    
    print(f"更新请求状态码: {update_response.status_code}")
    
    if update_response.status_code == 200:
        update_result = update_response.json()
        print(f"✅ 更新成功: {update_result.get('message', '')}")
        
        # 等待2秒
        time.sleep(2)
        
        # 4. 直接查询数据库检查图片数据
        print("\n4. 检查数据库...")
        import sys
        sys.path.append('.')
        from app.database import db_config
        
        query = """
        SELECT course, content, difficulty, 
               image_data IS NOT NULL as has_image_data,
               image_type,
               OCTET_LENGTH(image_data) as image_size
        FROM reminders WHERE id = %s
        """
        
        result = db_config.execute_query(query, (reminder_id,))
        
        if result:
            reminder = result[0]
            print(f"数据库查询结果:")
            print(f"  课程: {reminder['course']}")
            print(f"  内容: {reminder['content']}")
            print(f"  难度: {reminder['difficulty']}")
            print(f"  有图片数据: {reminder['has_image_data']}")
            print(f"  图片类型: {reminder['image_type']}")
            print(f"  图片大小: {reminder['image_size']} bytes")
            
            if reminder['has_image_data'] and reminder['image_size'] > 0:
                print("✅ 验证通过：提醒已正确更新，包含图片")
                return True
            else:
                print("❌ 验证失败：提醒更新后没有图片数据")
                return False
        else:
            print("❌ 数据库查询失败")
            return False
    else:
        print(f"❌ 更新失败: {update_response.status_code}")
        print(f"响应: {update_response.text[:500]}")
        return False

if __name__ == "__main__":
    success = test_direct_update()
    
    print()
    print("=" * 50)
    print("直接测试结果:", "✅ 通过" if success else "❌ 失败")
    print("=" * 50)
    
    if not success:
        import sys
        sys.exit(1)
