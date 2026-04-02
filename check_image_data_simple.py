#!/usr/bin/env python3
"""
简单检查image_data字段
"""

import os
os.environ['DB_TYPE'] = 'postgresql'

from app.database import db_config

def check_image_data():
    """检查image_data字段"""
    print("检查image_data字段...")
    
    # 简单查询，不使用LENGTH函数
    query = """
    SELECT id, course, content, 
           image_data IS NOT NULL as has_image_data,
           image_type
    FROM reminders 
    WHERE user_id LIKE 'simple_test_user_%' 
    ORDER BY created_at DESC 
    LIMIT 5
    """
    
    try:
        reminders = db_config.execute_query(query)
        print(f"找到 {len(reminders)} 个测试提醒:")
        for reminder in reminders:
            print(f"  ID: {reminder['id']}")
            print(f"    课程: {reminder['course']}")
            print(f"    有图片数据: {reminder['has_image_data']}")
            print(f"    图片类型: {reminder['image_type']}")
            
            # 如果有图片数据，检查实际大小
            if reminder['has_image_data']:
                size_query = """
                SELECT OCTET_LENGTH(image_data) as image_size
                FROM reminders 
                WHERE id = %s
                """
                size_result = db_config.execute_query(size_query, (reminder['id'],))
                if size_result:
                    print(f"    图片大小: {size_result[0]['image_size']} bytes")
                else:
                    print(f"    图片大小: 未知")
            print()
            
    except Exception as e:
        print(f"查询失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_image_data()
