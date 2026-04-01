#!/usr/bin/env python3
"""
测试外键约束修复
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import init_database, db_config
from app.models import SaveReminderRequest, HomeworkInfo
import uuid

# 初始化数据库
init_database()

# 测试数据
test_user_id = "test_user_001"
test_homework = HomeworkInfo(
    course="测试课程",
    content="测试作业内容",
    deadline="2026-04-10 23:59",
    start_time="2026-04-01 10:00",
    difficulty="中"
)

test_request = SaveReminderRequest(
    user_id=test_user_id,
    homework=test_homework
)

print("测试外键约束修复...")
print(f"数据库类型: {db_config.db_type}")
print(f"测试用户ID: {test_user_id}")

# 首先删除可能存在的测试数据（清理）
try:
    # 删除提醒
    delete_reminders_query = "DELETE FROM reminders WHERE user_id = %s"
    db_config.execute_query(delete_reminders_query, (test_user_id,))
    print("已清理旧提醒数据")
    
    # 删除用户
    delete_user_query = "DELETE FROM users WHERE user_id = %s"
    db_config.execute_query(delete_user_query, (test_user_id,))
    print("已清理旧用户数据")
except Exception as e:
    print(f"清理数据时出错（可能表不存在）: {e}")

# 测试1：检查用户是否存在
print("\n=== 测试1：检查用户是否存在 ===")
check_user_query = "SELECT user_id FROM users WHERE user_id = %s"
users_data = db_config.execute_query(check_user_query, (test_user_id,))
if users_data:
    print(f"❌ 用户 {test_user_id} 已存在（不应该存在）")
else:
    print(f"✅ 用户 {test_user_id} 不存在（正确）")

# 测试2：模拟创建提醒（应该自动创建用户）
print("\n=== 测试2：模拟创建提醒 ===")
reminder_id = str(uuid.uuid4())

# 首先确保用户存在（复制create_reminder中的逻辑）
try:
    users_data = db_config.execute_query(check_user_query, (test_user_id,))
    
    if not users_data:
        print(f"用户 {test_user_id} 不存在，创建默认用户")
        
        if db_config.db_type == "postgresql":
            create_user_query = """
            INSERT INTO users (user_id, openid, nick_name, avatar_url)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id) DO NOTHING
            """
        else:
            create_user_query = """
            INSERT OR IGNORE INTO users (user_id, openid, nick_name, avatar_url)
            VALUES (?, ?, ?, ?)
            """
        
        user_params = (
            test_user_id,
            test_user_id,
            f"用户{test_user_id[-4:]}",
            ""
        )
        
        db_config.execute_query(create_user_query, user_params)
        print(f"✅ 已创建默认用户: {test_user_id}")
    else:
        print(f"✅ 用户 {test_user_id} 已存在")
except Exception as user_error:
    print(f"❌ 创建用户失败: {user_error}")

# 测试3：创建提醒
print("\n=== 测试3：创建提醒 ===")
query = """
INSERT INTO reminders (id, user_id, course, content, start_time, deadline, difficulty, status)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

params = (
    reminder_id,
    test_user_id,
    test_homework.course,
    test_homework.content,
    test_homework.start_time,
    test_homework.deadline,
    test_homework.difficulty,
    'pending'
)

try:
    db_config.execute_query(query, params)
    print(f"✅ 创建提醒成功: {reminder_id}")
    
    # 验证提醒已创建
    check_reminder_query = "SELECT id FROM reminders WHERE id = %s"
    reminders_data = db_config.execute_query(check_reminder_query, (reminder_id,))
    if reminders_data:
        print(f"✅ 验证提醒存在: {reminder_id}")
    else:
        print(f"❌ 提醒创建失败: {reminder_id}")
        
except Exception as e:
    print(f"❌ 创建提醒失败: {e}")

# 测试4：验证用户已创建
print("\n=== 测试4：验证用户已创建 ===")
users_data = db_config.execute_query(check_user_query, (test_user_id,))
if users_data:
    print(f"✅ 用户 {test_user_id} 已成功创建")
else:
    print(f"❌ 用户 {test_user_id} 未创建")

# 测试5：获取提醒列表
print("\n=== 测试5：获取提醒列表 ===")
get_reminders_query = """
SELECT id, user_id, course, content, start_time, deadline, difficulty, status, created_at
FROM reminders 
WHERE user_id = %s
ORDER BY created_at DESC
"""

try:
    reminders_data = db_config.execute_query(get_reminders_query, (test_user_id,))
    print(f"✅ 获取到 {len(reminders_data)} 条提醒")
    for reminder in reminders_data:
        print(f"  - 提醒ID: {reminder['id']}, 课程: {reminder['course']}, 状态: {reminder['status']}")
except Exception as e:
    print(f"❌ 获取提醒列表失败: {e}")

print("\n=== 测试完成 ===")
print("如果所有测试都通过✅，则外键约束问题已修复。")
