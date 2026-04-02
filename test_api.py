import requests

# 获取用户的提醒列表
url = 'http://localhost:8002/api/reminders?user_id=test'
response = requests.get(url)
print(f'状态码: {response.status_code}')
data = response.json()

if data.get('success') and data.get('data'):
    reminders = data['data']
    if reminders:
        print(f'找到 {len(reminders)} 个提醒:')
        for i, reminder in enumerate(reminders[:3]):  # 只显示前3个
            print(f'{i+1}. ID: {reminder["id"]}, 课程: {reminder["course"]}, 截止时间: {reminder["deadline"]}')
    else:
        print('没有找到提醒')
else:
    print(f'获取失败: {data}')
