#!/usr/bin/env python3
"""
修复PostgreSQL数据库中的图片URL
将本地URL改为生产环境URL
"""

import os
import psycopg2
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def fix_image_urls_postgresql():
    """修复PostgreSQL数据库中的图片URL（将本地URL改为生产环境URL）"""
    
    # 获取数据库连接信息
    db_url = os.getenv("POSTGRES_EXTERNAL_URL")
    if not db_url:
        print("错误: 未找到POSTGRES_EXTERNAL_URL环境变量")
        return
    
    print(f"连接PostgreSQL数据库...")
    
    try:
        # 连接数据库
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # 查找所有包含本地URL的图片
        cursor.execute("""
            SELECT id, image_url 
            FROM reminders 
            WHERE image_url LIKE 'http://localhost:%/images/%' 
               OR image_url LIKE 'http://127.0.0.1:%/images/%'
               OR image_url LIKE 'localhost:%/images/%'
        """)
        
        rows = cursor.fetchall()
        print(f"找到 {len(rows)} 条需要修复的记录")
        
        # 修复每条记录
        for row_id, image_url in rows:
            if image_url:
                # 提取文件名
                filename = image_url.split('/')[-1]
                # 生成新的生产环境URL
                new_url = f"https://zhijireminderbackend.onrender.com/images/{filename}"
                
                # 更新数据库
                cursor.execute("""
                    UPDATE reminders 
                    SET image_url = %s 
                    WHERE id = %s
                """, (new_url, row_id))
                
                print(f"修复记录 {row_id}:")
                print(f"  原URL: {image_url}")
                print(f"  新URL: {new_url}")
        
        # 提交更改
        conn.commit()
        print(f"\n成功修复 {len(rows)} 条记录")
        
        # 关闭连接
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

def check_postgresql_urls():
    """检查PostgreSQL数据库中的图片URL"""
    
    # 获取数据库连接信息
    db_url = os.getenv("POSTGRES_EXTERNAL_URL")
    if not db_url:
        print("错误: 未找到POSTGRES_EXTERNAL_URL环境变量")
        return
    
    print(f"检查PostgreSQL数据库中的图片URL...")
    
    try:
        # 连接数据库
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # 获取所有图片URL
        cursor.execute("""
            SELECT id, course, image_url 
            FROM reminders 
            WHERE image_url IS NOT NULL AND image_url != ''
            ORDER BY id
        """)
        
        rows = cursor.fetchall()
        print(f"\n数据库中有 {len(rows)} 条包含图片URL的记录:")
        
        local_count = 0
        production_count = 0
        other_count = 0
        
        for row_id, course, image_url in rows:
            if 'localhost' in image_url or '127.0.0.1' in image_url:
                local_count += 1
                print(f"  - ID: {row_id}, 课程: {course}, URL: {image_url} [本地]")
            elif 'zhijireminderbackend.onrender.com' in image_url:
                production_count += 1
                print(f"  - ID: {row_id}, 课程: {course}, URL: {image_url} [生产]")
            else:
                other_count += 1
                print(f"  - ID: {row_id}, 课程: {course}, URL: {image_url} [其他]")
        
        print(f"\n统计:")
        print(f"  本地URL: {local_count} 条")
        print(f"  生产URL: {production_count} 条")
        print(f"  其他URL: {other_count} 条")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"检查数据库URL错误: {e}")

if __name__ == "__main__":
    print("=== PostgreSQL图片URL修复工具 ===")
    print("说明: 此工具将本地图片URL改为生产环境URL")
    
    print("\n1. 检查数据库中的图片URL")
    check_postgresql_urls()
    
    print("\n2. 修复数据库中的图片URL（本地→生产）")
    response = input("是否开始修复？(y/n): ")
    if response.lower() == 'y':
        fix_image_urls_postgresql()
    else:
        print("已取消修复操作")
    
    print("\n=== 操作完成 ===")
    print("提示: 修复后，请确保生产环境服务器上的images目录包含所有图片文件")
