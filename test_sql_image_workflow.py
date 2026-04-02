#!/usr/bin/env python3
"""
测试完整的SQL图片工作流：
1. 上传图片到SQL数据库
2. 从SQL数据库获取图片
3. 验证图片API端点
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

def test_sql_image_workflow():
    """测试完整的SQL图片工作流"""
    print("=== 测试完整的SQL图片工作流 ===")
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
        print(f"   Base64长度: {len(image_base64)} 字符")
        print()
    except FileNotFoundError:
        print(f"❌ 测试图片文件不存在: {test_image_path}")
        print("   请确保 downloaded_test_image.png 文件存在")
        return False
    except Exception as e:
        print(f"❌ 读取测试图片失败: {e}")
        return False
    
    # 2. 测试上传图片到SQL数据库（使用/upload-image-only端点）
    print("2. 测试上传图片到SQL数据库（使用/upload-image-only端点）")
    
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
                image_url = data.get('image_url')
                reminder_id = data.get('reminder_id')
                image_api_url = data.get('image_api_url')
                
                print(f"   图片URL: {image_url}")
                print(f"   提醒ID: {reminder_id}")
                print(f"   图片API URL: {image_api_url}")
                
                # 检查返回的URL是否是API URL
                if '/api/images/' in image_url:
                    print("   ✅ 返回的是API URL（图片在数据库中）")
                else:
                    print("   ⚠️ 返回的是文件URL（图片在文件系统中）")
                
                print()
                
                # 3. 验证图片是否真的保存到数据库
                print("3. 验证图片是否真的保存到数据库")
                
                try:
                    # 直接查询数据库
                    query = """
                    SELECT id, user_id, LENGTH(image_data) as image_size, image_type
                    FROM reminders 
                    WHERE id = %s
                    """
                    
                    db_result = db_config.execute_query(query, (reminder_id,))
                    
                    if db_result and len(db_result) > 0:
                        row = db_result[0]
                        db_image_size = row.get('image_size', 0)
                        db_image_type = row.get('image_type', '未知')
                        
                        print(f"   数据库查询成功:")
                        print(f"     ID: {row.get('id')}")
                        print(f"     用户: {row.get('user_id')}")
                        print(f"     图片大小: {db_image_size} bytes")
                        print(f"     图片类型: {db_image_type}")
                        
                        if db_image_size > 0:
                            print("   ✅ 图片已成功保存到数据库")
                        else:
                            print("   ❌ 图片大小为0，可能没有保存成功")
                            return False
                    else:
                        print("   ❌ 数据库中没有找到该记录")
                        return False
                        
                except Exception as db_error:
                    print(f"   ❌ 数据库查询失败: {db_error}")
                    return False
                
                print()
                
                # 4. 测试从SQL数据库获取图片
                print("4. 测试从SQL数据库获取图片")
                
                try:
                    # 使用图片API端点获取图片
                    image_response = requests.get(f"{base_url}{image_api_url}", timeout=10)
                    
                    print(f"   请求URL: {base_url}{image_api_url}")
                    print(f"   状态码: {image_response.status_code}")
                    print(f"   Content-Type: {image_response.headers.get('Content-Type')}")
                    print(f"   获取的图片大小: {len(image_response.content)} bytes")
                    
                    if image_response.status_code == 200:
                        # 验证获取的图片与原始图片是否相同
                        if len(image_response.content) == len(image_data):
                            print("   ✅ 获取的图片与原始图片大小相同")
                        else:
                            print(f"   ⚠️ 图片大小不匹配: 原始={len(image_data)} bytes, 获取={len(image_response.content)} bytes")
                        
                        # 检查Content-Type
                        content_type = image_response.headers.get('Content-Type', '')
                        if 'image/' in content_type:
                            print(f"   ✅ Content-Type正确: {content_type}")
                        else:
                            print(f"   ⚠️ Content-Type可能不正确: {content_type}")
                        
                        print("   ✅ 图片API端点工作正常")
                    else:
                        print(f"   ❌ 图片API端点返回错误: {image_response.status_code}")
                        print(f"   响应内容: {image_response.text[:200]}")
                        return False
                        
                except Exception as api_error:
                    print(f"   ❌ 获取图片失败: {api_error}")
                    return False
                
                print()
                
                # 5. 测试获取提醒列表，验证图片URL是否正确
                print("5. 测试获取提醒列表，验证图片URL是否正确")
                
                try:
                    reminders_response = requests.get(f"{base_url}/api/reminders?user_id={user_id}", timeout=10)
                    
                    if reminders_response.status_code == 200:
                        reminders_result = reminders_response.json()
                        reminders = reminders_result.get('data', [])
                        
                        print(f"   找到 {len(reminders)} 条提醒")
                        
                        # 查找我们刚刚创建的提醒
                        found = False
                        for reminder in reminders:
                            if reminder.get('id') == reminder_id:
                                found = True
                                print(f"   找到测试提醒:")
                                print(f"     ID: {reminder.get('id')}")
                                print(f"     课程: {reminder.get('course')}")
                                print(f"     图片URL: {reminder.get('image_url')}")
                                
                                # 检查图片URL是否是API URL
                                if reminder.get('image_url') and '/api/images/' in reminder.get('image_url', ''):
                                    print("     ✅ 图片URL是API URL（正确）")
                                else:
                                    print("     ⚠️ 图片URL不是API URL")
                                break
                        
                        if not found:
                            print("   ❌ 在提醒列表中未找到测试提醒")
                            return False
                    else:
                        print(f"   ❌ 获取提醒列表失败: {reminders_response.status_code}")
                        return False
                        
                except Exception as reminders_error:
                    print(f"   ❌ 获取提醒列表失败: {reminders_error}")
                    return False
                
                print()
                print("=== 测试总结 ===")
                print("✅ 所有测试通过！")
                print(f"   图片已成功保存到SQL数据库")
                print(f"   图片API端点正常工作: {base_url}{image_api_url}")
                print(f"   前端可以通过此URL访问图片")
                print(f"   用户ID: {user_id}")
                print(f"   提醒ID: {reminder_id}")
                
                return True
            else:
                print(f"   上传失败: {result.get('message', '未知错误')}")
                return False
        else:
            print(f"   请求失败: {response.status_code}")
            print(f"   响应: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ 上传图片失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_sql_image_workflow()
    if success:
        print("\n🎉 测试成功！图片已成功保存到SQL数据库并从SQL数据库获取。")
        print("   前端现在应该可以正常显示图片了。")
    else:
        print("\n❌ 测试失败！请检查错误信息。")
    
    sys.exit(0 if success else 1)
