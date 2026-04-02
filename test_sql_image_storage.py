#!/usr/bin/env python3
"""
测试图片存储到SQL数据库的功能
验证图片是否保存到数据库而不是文件系统
"""

import requests
import base64
import json
import os

def test_sql_image_storage():
    """测试图片存储到SQL数据库的功能"""
    
    # 本地测试URL
    base_url = "http://localhost:8002"
    
    print("=== 测试图片存储到SQL数据库功能 ===")
    print(f"API地址: {base_url}")
    print()
    
    # 1. 测试上传图片到数据库（使用修改后的/upload-image-only）
    print("1. 测试上传图片到数据库（使用/upload-image-only）...")
    
    # 读取一个测试图片文件
    test_image_path = "downloaded_test_image.png"
    try:
        with open(test_image_path, "rb") as f:
            image_data = f.read()
        
        # 转换为base64（不带data URL前缀）
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # 准备请求数据
        request_data = {
            "image": image_base64,  # 只发送base64，不带data URL前缀
            "user_id": "test"
        }
        
        # 发送请求到修改后的API
        response = requests.post(
            f"{base_url}/api/upload-image-only",
            json=request_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   成功: {result.get('success', False)}")
            if result.get('success'):
                data = result.get('data', {})
                image_url = data.get('image_url')
                reminder_id = data.get('reminder_id')
                image_api_url = data.get('image_api_url')
                print(f"   图片URL: {image_url}")
                print(f"   提醒ID: {reminder_id}")
                print(f"   图片API URL: {image_api_url}")
                
                # 检查返回的URL是否是API URL而不是文件URL
                if '/api/images/' in image_url:
                    print("   ✅ 返回的是API URL（图片在数据库中）")
                else:
                    print("   ⚠️ 返回的是文件URL（图片在文件系统中）")
                
                # 2. 测试获取图片
                print("\n2. 测试获取图片...")
                image_response = requests.get(f"{base_url}{image_api_url}", timeout=10)
                print(f"   状态码: {image_response.status_code}")
                print(f"   Content-Type: {image_response.headers.get('Content-Type')}")
                print(f"   图片大小: {len(image_response.content)} bytes")
                
                # 3. 检查文件系统是否有图片文件
                print("\n3. 检查文件系统...")
                if '/images/' in image_url:
                    # 提取文件名
                    import urllib.parse
                    filename = image_url.split('/')[-1]
                    file_path = os.path.join('images', filename)
                    if os.path.exists(file_path):
                        print(f"   ⚠️ 图片文件存在: {file_path}")
                        print(f"     文件大小: {os.path.getsize(file_path)} bytes")
                    else:
                        print(f"   ✅ 图片文件不存在（正确，图片在数据库中）")
                
                # 4. 测试获取提醒列表
                print("\n4. 测试获取提醒列表...")
                reminders_response = requests.get(f"{base_url}/api/reminders?user_id=test", timeout=10)
                if reminders_response.status_code == 200:
                    reminders_result = reminders_response.json()
                    reminders = reminders_result.get('data', [])
                    print(f"   找到 {len(reminders)} 条提醒")
                    
                    # 查找我们刚刚创建的提醒
                    for reminder in reminders:
                        if reminder.get('id') == reminder_id:
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
                else:
                    print(f"   获取提醒列表失败: {reminders_response.status_code}")
            else:
                print(f"   上传失败: {result.get('message', '未知错误')}")
        else:
            print(f"   请求失败: {response.status_code}")
            print(f"   响应: {response.text}")
            
    except FileNotFoundError:
        print(f"   测试图片文件不存在: {test_image_path}")
        print("   请先运行其他测试或上传一个图片文件")
    except Exception as e:
        print(f"   测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. 测试原有的/upload-image-binary端点（确保它仍然工作）
    print("\n5. 测试原有的/upload-image-binary端点...")
    try:
        with open(test_image_path, "rb") as f:
            image_data = f.read()
        
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        request_data = {
            "image": f"data:image/png;base64,{image_base64}",
            "user_id": "test2"
        }
        
        response = requests.post(
            f"{base_url}/api/upload-image-binary",
            json=request_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   成功: {result.get('success', False)}")
            if result.get('success'):
                data = result.get('data', {})
                print(f"   提醒ID: {data.get('reminder_id')}")
                print(f"   图片API URL: {data.get('image_api_url')}")
                print("   ✅ /upload-image-binary端点工作正常")
        else:
            print(f"   请求失败: {response.status_code}")
    except Exception as e:
        print(f"   测试失败: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_sql_image_storage()
