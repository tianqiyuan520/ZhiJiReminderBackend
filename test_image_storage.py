#!/usr/bin/env python3
"""
测试图片存储到数据库的功能
"""

import requests
import base64
import json

def test_image_storage():
    """测试图片存储到数据库的功能"""
    
    # 本地测试URL
    base_url = "http://localhost:8003"
    
    print("=== 测试图片存储到数据库功能 ===")
    print(f"API地址: {base_url}")
    print()
    
    # 1. 测试上传图片到数据库
    print("1. 测试上传图片到数据库...")
    
    # 读取一个测试图片文件
    test_image_path = "downloaded_test_image.png"
    try:
        with open(test_image_path, "rb") as f:
            image_data = f.read()
        
        # 转换为base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # 准备请求数据
        request_data = {
            "image": f"data:image/png;base64,{image_base64}",
            "user_id": "test"
        }
        
        # 发送请求
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
                reminder_id = data.get('reminder_id')
                image_api_url = data.get('image_api_url')
                print(f"   提醒ID: {reminder_id}")
                print(f"   图片API URL: {image_api_url}")
                
                # 2. 测试获取图片
                print("\n2. 测试获取图片...")
                image_response = requests.get(f"{base_url}{image_api_url}", timeout=10)
                print(f"   状态码: {image_response.status_code}")
                print(f"   Content-Type: {image_response.headers.get('Content-Type')}")
                print(f"   图片大小: {len(image_response.content)} bytes")
                
                # 3. 测试获取提醒列表
                print("\n3. 测试获取提醒列表...")
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
                            print(f"     是否有图片数据: {'是' if reminder.get('image_data') else '否'}")
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
    
    # 4. 测试现有的图片API端点
    print("\n4. 测试现有的图片API端点...")
    
    # 先获取一个现有的提醒ID
    try:
        reminders_response = requests.get(f"{base_url}/api/reminders?user_id=test", timeout=10)
        if reminders_response.status_code == 200:
            reminders_result = reminders_response.json()
            reminders = reminders_result.get('data', [])
            
            if reminders:
                # 使用第一个有图片的提醒
                for reminder in reminders:
                    if reminder.get('image_url'):
                        test_reminder_id = reminder.get('id')
                        print(f"   使用提醒ID: {test_reminder_id}")
                        
                        # 测试图片API
                        image_api_url = f"{base_url}/api/images/{test_reminder_id}"
                        image_response = requests.get(image_api_url, timeout=10)
                        print(f"   图片API状态码: {image_response.status_code}")
                        print(f"   图片API Content-Type: {image_response.headers.get('Content-Type')}")
                        break
                else:
                    print("   没有找到有图片的提醒")
            else:
                print("   没有找到提醒")
        else:
            print(f"   获取提醒列表失败: {reminders_response.status_code}")
    except Exception as e:
        print(f"   测试现有API失败: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_image_storage()
