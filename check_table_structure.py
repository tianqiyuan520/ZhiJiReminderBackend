#!/usr/bin/env python3
"""
检查数据库表结构
"""

import os
os.environ['DB_TYPE'] = 'postgresql'

from app.database import db_config

def check_reminders_table():
    """检查reminders表结构"""
    print("检查reminders表结构...")
    
    # 检查表结构
    query = """
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns 
    WHERE table_name = 'reminders' 
    ORDER BY ordinal_position
    """
    
    try:
        result = db_config.execute_query(query)
        print(f"reminders表有 {len(result)} 列:")
        for row in result:
            print(f"  {row['column_name']}: {row['data_type']} (nullable: {row['is_nullable']})")
        
        # 检查特定提醒的image_data字段
        print("\n检查特定提醒的image_data字段...")
        check_query = """
        SELECT id, course, content, 
               image_data IS NOT NULL as has_image_data,
               image_type,
               LENGTH(image_data) as image_size
        FROM reminders 
        WHERE user_id LIKE 'simple_test_user_%' 
        ORDER BY created_at DESC 
        LIMIT 5
        """
        
        reminders = db_config.execute_query(check_query)
        print(f"找到 {len(reminders)} 个测试提醒:")
        for reminder in reminders:
            print(f"  ID: {reminder['id']}")
            print(f"    课程: {reminder['course']}")
            print(f"    有图片数据: {reminder['has_image_data']}")
            print(f"    图片类型: {reminder['image_type']}")
            print(f"    图片大小: {reminder['image_size']} bytes")
            print()
            
    except Exception as e:
        print(f"查询失败: {e}")

def check_database_type():
    """检查数据库类型"""
    print(f"当前数据库类型: {db_config.db_type}")
    # 不打印连接字符串，因为它可能包含敏感信息

if __name__ == "__main__":
    check_database_type()
    print()
    check_reminders_table()
