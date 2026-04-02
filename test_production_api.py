#!/usr/bin/env python3
"""
测试生产环境API
"""

import requests
import json

def test_production_api():
    """测试生产环境API"""
    
    # 生产环境API地址
    base_url = "https://zhijireminderbackend.onrender.com"
    
    print(f"测试生产环境API: {base_url}")
    print("=" * 50)
    
    try:
        # 测试首页
        print("1. 测试首页...")
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.text[:100]}...")
        
        # 测试获取提醒（使用默认用户test）
        print("\n2. 测试获取提醒...")
        response = requests.get(f"{base_url}/api/reminders?user_id=test", timeout=10)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   成功: {data.get('success', False)}")
            reminders = data.get('data', [])
            print(f"   找到 {len(reminders)} 条提醒")
            
            # 检查图片URL
            local_urls = []
            production_urls = []
            other_urls = []
            
            for reminder in reminders:
                image_url = reminder.get('image_url', '')
                if image_url:
                    if 'localhost' in image_url or '127.0.0.1' in image_url:
                        local_urls.append(image_url)
                    elif 'zhijireminderbackend.onrender.com' in image_url:
                        production_urls.append(image_url)
                    else:
                        other_urls.append(image_url)
            
            print(f"\n   图片URL统计:")
            print(f"     本地URL: {len(local_urls)} 条")
            print(f"     生产URL: {len(production_urls)} 条")
            print(f"     其他URL: {len(other_urls)} 条")
            
            if local_urls:
                print(f"\n   本地URL示例:")
                for url in local_urls[:3]:  # 显示前3个
                    print(f"     - {url}")
        
        # 测试上传图片API端点是否存在
        print("\n3. 测试上传图片API...")
        try:
            response = requests.post(f"{base_url}/api/upload-image-only", 
                                   json={"image": "test", "user_id": "test"}, 
                                   timeout=10)
            print(f"   状态码: {response.status_code}")
            if response.status_code == 400:
                print("   正常: 图片数据为空错误（预期行为）")
        except Exception as e:
            print(f"   错误: {e}")
            
    except requests.exceptions.Timeout:
        print("错误: 请求超时，生产环境API可能未运行或网络问题")
    except requests.exceptions.ConnectionError:
        print("错误: 连接失败，生产环境API可能未运行")
    except Exception as e:
        print(f"错误: {e}")
    
    print("\n" + "=" * 50)
    print("测试完成")

if __name__ == "__main__":
    test_production_api()
