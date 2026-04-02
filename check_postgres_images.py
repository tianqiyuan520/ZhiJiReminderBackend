#!/usr/bin/env python3
"""
检查PostgreSQL数据库中的图片数据
"""

import sys
import os
sys.path.append('.')

# 设置环境变量确保使用PostgreSQL
os.environ['DB_TYPE'] = 'postgresql'

from app.database import db_config

def check_postgres_images():
    """检查PostgreSQL数据库中的图片数据"""
    print("=== 检查PostgreSQL数据库中的图片数据 ===")
    
    try:
        # 查询所有提醒（包括是否有图片数据）
        query = """
        SELECT id, user_id, 
               CASE WHEN image_data IS NULL THEN '无图片' ELSE '有图片' END as has_image,
               LENGTH(image_data) as image_size,
               image_type
        FROM reminders 
        ORDER BY created_at DESC
        LIMIT 10
        """
        
        result = db_config.execute_query(query)
        
        print(f"找到 {len(result)} 条提醒记录")
        print()
        
        if len(result) == 0:
            print("❌ 数据库中没有提醒记录！")
            return False
        
        # 显示记录
        print("前10条提醒记录:")
        print("-" * 80)
        print(f"{'ID':36} | {'用户':10} | {'图片状态':8} | {'图片大小':10} | {'图片类型':15}")
        print("-" * 80)
        
        has_images = False
        for row in result:
            reminder_id = row.get('id', '')[:36]
            user_id = row.get('user_id', '')[:10]
            has_image = row.get('has_image', '无图片')
            image_size = row.get('image_size', 0)
            image_type = row.get('image_type', '未知')
            
            if has_image == '有图片':
                has_images = True
                print(f"{reminder_id} | {user_id:10} | {has_image:8} | {image_size:10} | {image_type:15}")
            else:
                print(f"{reminder_id} | {user_id:10} | {has_image:8} | {'-':10} | {'-':15}")
        
        print("-" * 80)
        
        if not has_images:
            print("❌ 数据库中没有包含图片数据的提醒！")
            print()
            print("可能的原因：")
            print("1. 图片没有保存到数据库（可能保存到了文件系统）")
            print("2. 上传图片时使用了错误的API端点")
            print("3. 数据库表结构有问题")
            return False
        
        # 检查具体的图片数据
        print()
        print("=== 检查具体的图片数据 ===")
        
        # 查找有图片数据的记录
        image_query = """
        SELECT id, user_id, image_type
        FROM reminders 
        WHERE image_data IS NOT NULL
        LIMIT 3
        """
        
        image_result = db_config.execute_query(image_query)
        
        if len(image_result) > 0:
            print(f"找到 {len(image_result)} 条包含图片数据的记录:")
            for i, row in enumerate(image_result):
                print(f"{i+1}. ID: {row.get('id')}, 用户: {row.get('user_id')}, 类型: {row.get('image_type')}")
            
            # 测试第一个图片的API端点
            first_id = image_result[0].get('id')
            print()
            print(f"测试图片API端点: /api/images/{first_id}")
            print(f"URL: http://localhost:8002/api/images/{first_id}")
            
            return True
        else:
            print("❌ 虽然查询显示有图片，但详细检查发现没有图片数据")
            return False
            
    except Exception as e:
        print(f"❌ 查询数据库失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_postgres_images()
    sys.exit(0 if success else 1)
