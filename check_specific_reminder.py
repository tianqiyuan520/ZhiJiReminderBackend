#!/usr/bin/env python3
"""
检查特定提醒
"""

import os
os.environ['DB_TYPE'] = 'postgresql'

from app.database import db_config

def check_specific_reminder():
    """检查特定提醒"""
    print("检查特定提醒...")
    
    # 检查我们刚刚创建的提醒
    reminder_id = "393034e3-8d11-493f-ba2e-dcdaeb2f6c0c"  # 从日志中获取的ID
    
    # 简单查询
    query = "SELECT id, course, content, image_data IS NOT NULL as has_image_data FROM reminders WHERE id = %s"
    
    try:
        result = db_config.execute_query(query, (reminder_id,))
        if result:
            reminder = result[0]
            print(f"提醒ID: {reminder['id']}")
            print(f"课程: {reminder['course']}")
            print(f"内容: {reminder['content']}")
            print(f"有图片数据: {reminder['has_image_data']}")
            
            # 如果有图片数据，获取实际数据
            if reminder['has_image_data']:
                data_query = "SELECT image_data, image_type FROM reminders WHERE id = %s"
                data_result = db_config.execute_query(data_query, (reminder_id,))
                if data_result:
                    image_data = data_result[0]['image_data']
                    image_type = data_result[0]['image_type']
                    print(f"图片类型: {image_type}")
                    print(f"图片数据大小: {len(image_data) if image_data else 0} bytes")
                    
                    # 检查是否是有效的图片数据
                    if image_data:
                        try:
                            import base64
                            # 尝试解码为base64
                            encoded = base64.b64encode(image_data[:100]).decode('utf-8')
                            print(f"图片数据前100字节的base64: {encoded[:50]}...")
                        except:
                            print("无法编码图片数据")
                else:
                    print("无法获取图片数据详情")
        else:
            print(f"未找到提醒: {reminder_id}")
            
    except Exception as e:
        print(f"查询失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_specific_reminder()
