#!/usr/bin/env python3
"""
检查数据库中的图片数据
"""

import sys
sys.path.append('.')

from app.database import db_config

def check_image_data():
    """检查数据库中的图片数据"""
    print("=== 检查数据库中的图片数据 ===")
    
    # 查询所有包含图片数据的提醒
    query = 'SELECT id, user_id, image_data, image_type FROM reminders WHERE image_data IS NOT NULL'
    result = db_config.execute_query(query)
    
    print(f"找到 {len(result)} 条包含图片数据的提醒")
    print()
    
    if len(result) == 0:
        print("❌ 数据库中没有图片数据！")
        print("可能的原因：")
        print("1. 图片没有保存到数据库")
        print("2. 图片保存到了文件系统而不是数据库")
        print("3. 数据库查询有问题")
        return False
    
    # 显示前3条记录
    for i, row in enumerate(result[:3]):
        print(f"记录 {i+1}:")
        print(f"  ID: {row.get('id')}")
        print(f"  用户: {row.get('user_id')}")
        image_data = row.get('image_data')
        if image_data:
            print(f"  图片大小: {len(image_data)} bytes")
        else:
            print(f"  图片大小: 0 bytes (空数据)")
        print(f"  图片类型: {row.get('image_type', '未知')}")
        print()
    
    # 检查文件系统中是否有图片文件
    print("=== 检查文件系统中的图片文件 ===")
    import os
    images_dir = "images"
    if os.path.exists(images_dir):
        image_files = [f for f in os.listdir(images_dir) if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
        print(f"images目录中有 {len(image_files)} 个图片文件")
        if image_files:
            print("前5个文件:")
            for f in image_files[:5]:
                file_path = os.path.join(images_dir, f)
                size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                print(f"  {f} ({size} bytes)")
    else:
        print(f"images目录不存在")
    
    print()
    print("=== 测试图片API端点 ===")
    
    # 测试第一个图片的API端点
    if len(result) > 0:
        first_id = result[0].get('id')
        print(f"测试图片API: /api/images/{first_id}")
        print(f"URL: http://localhost:8002/api/images/{first_id}")
        
        # 检查服务器是否在运行
        import requests
        try:
            response = requests.get(f"http://localhost:8002/api/images/{first_id}", timeout=5)
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
        print("❌ 没有图片数据可测试")
        return False

if __name__ == "__main__":
    success = check_image_data()
    sys.exit(0 if success else 1)
