#!/usr/bin/env python3
"""
直接测试图片保存到PostgreSQL数据库
"""

import sys
import os
import base64
import uuid

# 设置环境变量确保使用PostgreSQL
os.environ['DB_TYPE'] = 'postgresql'

sys.path.append('.')
from app.database import db_config

def test_direct_image_save():
    """直接测试图片保存到数据库"""
    print("=== 直接测试图片保存到PostgreSQL数据库 ===")
    
    # 读取测试图片
    test_image_path = "downloaded_test_image.png"
    try:
        with open(test_image_path, "rb") as f:
            image_data = f.read()
        
        print(f"测试图片大小: {len(image_data)} bytes")
        
        # 生成唯一的提醒ID
        reminder_id = str(uuid.uuid4())
        user_id = "test_user"
        
        # 创建提醒记录（只包含图片数据）
        query = """
        INSERT INTO reminders (
            id, user_id, course, content, start_time, deadline, 
            difficulty, status, image_data, image_type
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            reminder_id,
            user_id,
            "测试课程",
            "测试内容",
            "",
            "未指定",
            "中",
            'pending',
            image_data,
            'image/png'
        )
        
        print(f"执行数据库插入...")
        print(f"提醒ID: {reminder_id}")
        print(f"用户ID: {user_id}")
        
        try:
            # 执行插入
            rowcount = db_config.execute_query(query, params)
            print(f"插入成功，影响行数: {rowcount}")
            
            # 验证插入
            verify_query = """
            SELECT id, user_id, LENGTH(image_data) as image_size, image_type
            FROM reminders 
            WHERE id = %s
            """
            
            verify_result = db_config.execute_query(verify_query, (reminder_id,))
            
            if verify_result and len(verify_result) > 0:
                row = verify_result[0]
                print(f"验证成功:")
                print(f"  ID: {row.get('id')}")
                print(f"  用户: {row.get('user_id')}")
                print(f"  图片大小: {row.get('image_size')} bytes")
                print(f"  图片类型: {row.get('image_type')}")
                
                # 测试图片API端点
                print()
                print("=== 测试图片API端点 ===")
                print(f"URL: http://localhost:8002/api/images/{reminder_id}")
                
                import requests
                try:
                    response = requests.get(f"http://localhost:8002/api/images/{reminder_id}", timeout=5)
                    print(f"状态码: {response.status_code}")
                    print(f"Content-Type: {response.headers.get('Content-Type')}")
                    print(f"图片大小: {len(response.content)} bytes")
                    
                    if response.status_code == 200:
                        print("✅ 图片API端点工作正常")
                        return True
                    else:
                        print(f"❌ 图片API端点返回错误: {response.status_code}")
                        return False
                except Exception as e:
                    print(f"❌ 无法连接到图片API: {e}")
                    return False
            else:
                print("❌ 验证失败：插入的记录不存在")
                return False
                
        except Exception as e:
            print(f"❌ 数据库插入失败: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except FileNotFoundError:
        print(f"❌ 测试图片文件不存在: {test_image_path}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_direct_image_save()
    sys.exit(0 if success else 1)
